from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import pandas as pd
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import bitcoin_hash_hex, bits_to_target, double_sha256, leading_zero_bits
from modules.ui import concept_flow, metric_explainer_grid, module_header, story_panel, styled_table, takeaway


@dataclass(frozen=True, slots=True)
class ParsedBlockHeader:
    raw_hex: str
    version: int
    previous_hash: str
    merkle_root: str
    timestamp: int
    bits: int
    nonce: int
    local_hash: str
    hash_value: int
    target: int

    @property
    def timestamp_utc(self) -> str:
        return datetime.fromtimestamp(self.timestamp, UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

    @property
    def target_hex(self) -> str:
        return f"{self.target:064x}"

    @property
    def is_valid_pow(self) -> bool:
        return self.hash_value <= self.target


def parse_block_header(header: bytes) -> ParsedBlockHeader:
    if len(header) != 80:
        raise ValueError(f"Expected an 80-byte Bitcoin block header, got {len(header)} bytes.")

    version = int.from_bytes(header[0:4], "little", signed=True)
    previous_hash = header[4:36][::-1].hex()
    merkle_root = header[36:68][::-1].hex()
    timestamp = int.from_bytes(header[68:72], "little")
    bits = int.from_bytes(header[72:76], "little")
    nonce = int.from_bytes(header[76:80], "little")
    digest = double_sha256(header)
    local_hash = bitcoin_hash_hex(digest)

    return ParsedBlockHeader(
        raw_hex=header.hex(),
        version=version,
        previous_hash=previous_hash,
        merkle_root=merkle_root,
        timestamp=timestamp,
        bits=bits,
        nonce=nonce,
        local_hash=local_hash,
        hash_value=int.from_bytes(digest, "little"),
        target=bits_to_target(bits),
    )


@st.cache_data(ttl=60, show_spinner=False)
def load_latest_header() -> tuple[dict[str, object], ParsedBlockHeader]:
    client = get_client()
    latest_block = client.get_latest_block()
    raw_block = client.get_block_raw(str(latest_block["id"]))
    parsed_header = parse_block_header(raw_block[:80])
    return latest_block, parsed_header


def render_m2() -> None:
    module_header(
        "Bloque por dentro",
        "Anatomia de un bloque valido",
        "Descarga el ultimo bloque, separa su header de 80 bytes y verifica localmente su Proof of Work.",
    )

    try:
        latest_block, header = load_latest_header()
    except BlockchainApiError as exc:
        st.error(f"No se pudo cargar el ultimo bloque desde las fuentes publicas: {exc}")
        return
    except Exception as exc:
        st.error(f"Error inesperado al verificar el header: {exc}")
        return

    hash_matches_api = header.local_hash == latest_block["id"]
    valid_pow = header.is_valid_pow and hash_matches_api

    story_panel(
        "Por que mirar el header",
        "El header es la parte pequeña del bloque que concentra la prueba criptografica.",
        "Un bloque completo puede contener muchas transacciones, pero los mineros no prueban el bloque entero una y otra vez: "
        "trabajan sobre un header de 80 bytes. Si el doble SHA-256 de ese header queda por debajo del objetivo, el bloque demuestra trabajo.",
        [
            "El hash anterior conecta este bloque con la cadena.",
            "La raiz de Merkle es un resumen criptografico de todas las transacciones del bloque.",
            "La verificacion PoW comprueba que el hash del header cumple el objetivo de dificultad.",
            "El nonce es una de las piezas que el minero puede cambiar para buscar un hash valido.",
        ],
    )
    concept_flow(
        [
            ("Descargar", "Se obtiene el bloque crudo desde una fuente publica de Bitcoin."),
            ("Separar", "Se toman los primeros 80 bytes, que forman el header."),
            ("Hashear", "Se calcula SHA256(SHA256(header)) localmente."),
            ("Comparar", "El resultado debe coincidir con el bloque publicado y ser menor que el objetivo."),
        ]
    )

    metric_explainer_grid(
        [
            (
                "Altura",
                f"{int(latest_block['height']):,}",
                "Numero del bloque contado desde el primer bloque de Bitcoin.",
            ),
            (
                "Tamano header",
                "80 bytes",
                "Parte pequena que se hashea para demostrar trabajo.",
            ),
            (
                "Ceros iniciales",
                str(leading_zero_bits(header.hash_value)),
                "Bits a cero al inicio del hash: senal de que el hash es muy pequeno.",
            ),
            (
                "Verificacion PoW",
                "Valida" if valid_pow else "Revisar",
                "El hash calculado aqui coincide con el publicado y queda por debajo del objetivo.",
            ),
        ]
    )
    st.write(
        "La metrica clave es la verificacion PoW. Si aparece como valida, significa que esta app ha recalculado el hash del bloque "
        "y ha comprobado que cumple la regla: el valor numerico del hash queda por debajo del objetivo de dificultad."
    )

    st.markdown("#### Los seis campos del header")
    st.write(
        "Estos son los datos exactos que entran en el hash. La tabla no esta para decorar: permite auditar que informacion se esta verificando."
    )
    field_rows = [
        ("Version", str(header.version), "Formato/reglas usadas por el bloque"),
        ("Hash anterior", header.previous_hash, "Enlace criptografico con el bloque previo"),
        (
            "Raiz de Merkle",
            header.merkle_root,
            "Hash resumen de las transacciones: permite detectar si alguna transaccion del bloque cambiara.",
        ),
        ("Timestamp", f"{header.timestamp} ({header.timestamp_utc})", "Hora declarada por el minero"),
        ("Bits", f"{header.bits} / 0x{header.bits:08x}", "Objetivo de dificultad en formato compacto"),
        ("Nonce", str(header.nonce), "Valor que ayuda a buscar un hash valido"),
    ]
    styled_table(
        pd.DataFrame(field_rows, columns=["Campo", "Valor", "Que significa"]),
    )

    st.markdown("#### Verificacion local con doble SHA-256")
    st.write(
        "Esta parte comprueba el bloque paso a paso. Primero la app calcula de nuevo el hash del header. "
        "Luego mira si ese hash coincide con el hash oficial del bloque. Por ultimo, comprueba la regla de dificultad: "
        "el hash debe ser menor que el objetivo. Si ambas comparaciones salen bien, el Proof of Work es valido."
    )
    st.code("hash = SHA256(SHA256(80-byte header))", language="text")
    st.markdown("#### Lectura de la comprobacion")
    st.write(
        "Las dos cajas de la izquierda deben ser iguales. Eso demuestra que el hash se ha reproducido correctamente. "
        "La caja de la derecha muestra el limite maximo permitido por la dificultad; el resultado `True` significa que el hash queda por debajo de ese limite."
    )
    verify_col_1, verify_col_2 = st.columns(2)
    with verify_col_1:
        st.write("Hash oficial del bloque")
        st.code(str(latest_block["id"]), language="text")
        st.write("Hash recalculado por esta app")
        st.code(header.local_hash, language="text")
    with verify_col_2:
        st.write("Objetivo maximo permitido")
        st.code(header.target_hex, language="text")
        st.write("El hash queda por debajo de ese objetivo")
        st.success("Si" if header.hash_value <= header.target else "No")

    if valid_pow:
        takeaway(
            "El bloque pasa la verificacion.",
            "El hash calculado localmente coincide con el hash publicado y ademas esta por debajo del objetivo. Eso es exactamente lo que significa que el bloque tiene Proof of Work valido.",
            tone="success",
        )
    else:
        st.error("La verificacion local ha fallado. Habria que revisar el orden de bytes, el bloque crudo o la respuesta de la fuente publica.")

    with st.expander("Header crudo de 80 bytes"):
        st.code(header.raw_hex, language="text")
