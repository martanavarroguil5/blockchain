from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import (
    bits_to_target,
    estimate_hash_rate_hs,
    human_difficulty,
    human_hash_rate,
    leading_zero_bits,
)
from modules.ui import metric_explainer_grid, module_header, story_panel, style_chart, takeaway


@st.cache_data(ttl=60, show_spinner=False)
def load_pow_snapshot(block_limit: int = 40) -> dict[str, object]:
    client = get_client()
    latest_block = client.get_latest_block()
    recent_blocks = client.get_recent_blocks_window(limit=block_limit)

    blocks_df = pd.DataFrame(recent_blocks).sort_values("height").reset_index(drop=True)
    blocks_df["timestamp_dt"] = pd.to_datetime(blocks_df["timestamp"], unit="s", utc=True)
    blocks_df["minutes_since_prev"] = blocks_df["timestamp"].diff() / 60

    latest_bits = int(latest_block["bits"])
    target = bits_to_target(latest_bits)
    hash_rate_hs = estimate_hash_rate_hs(float(latest_block["difficulty"]))

    return {
        "latest_block": latest_block,
        "recent_blocks": blocks_df,
        "target": target,
        "target_hex": f"{target:064x}",
        "target_leading_zero_bits": leading_zero_bits(target),
        "hash_rate_hs": hash_rate_hs,
    }


def render_m1() -> None:
    st_autorefresh(interval=60_000, key="m1_autorefresh")
    module_header(
        "Red en directo",
        "La red Bitcoin ahora mismo",
        "Metricas en directo para entender cuanto trabajo exige minar un bloque hoy.",
    )

    try:
        snapshot = load_pow_snapshot()
    except BlockchainApiError as exc:
        st.error(f"No se pudieron cargar los datos publicos de Bitcoin: {exc}")
        return
    except Exception as exc:
        st.error(f"Error inesperado al preparar esta vista: {exc}")
        return

    latest_block = snapshot["latest_block"]
    recent_blocks = snapshot["recent_blocks"]
    if not isinstance(latest_block, dict) or not isinstance(recent_blocks, pd.DataFrame):
        st.error("La fuente de datos devolvio un formato inesperado.")
        return

    now_utc = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    st.caption(f"Instantanea generada a las {now_utc}. Actualizacion automatica: 60 segundos.")
    story_panel(
        "Antes de mirar numeros",
        "Que indican estas metricas",
        "Esta pantalla resume el estado actual de Bitcoin. La altura dice cual es el ultimo bloque aceptado; "
        "la dificultad indica lo exigente que es encontrar un hash valido; el hash rate estima cuanta potencia de calculo "
        "esta compitiendo en la red; y las transacciones muestran cuanta actividad se incluyo en ese bloque. "
        "Juntas, estas cifras permiten ver si la red avanza con normalidad y cuanto trabajo sostiene cada bloque.",
    )

    metric_explainer_grid(
        [
            (
                "Ultima altura",
                f"{int(latest_block['height']):,}",
                "Numero del ultimo bloque aceptado por la red; indica hasta donde ha avanzado Bitcoin.",
            ),
            (
                "Dificultad",
                human_difficulty(float(latest_block["difficulty"])),
                "Multiplicador frente al nivel base: 134 T significa unas 134 billones de veces mas intentos de media.",
            ),
            (
                "Hash rate estimado",
                human_hash_rate(float(snapshot["hash_rate_hs"])),
                "Potencia de calculo aproximada compitiendo en la red; mas alta implica mas seguridad economica.",
            ),
            (
                "Transacciones",
                f"{int(latest_block['tx_count']):,}",
                "Operaciones incluidas en el ultimo bloque; resume la actividad confirmada en esa pieza.",
            ),
        ]
    )

    target_hex = str(snapshot["target_hex"])
    st.markdown("#### La dificultad convertida en objetivo")
    st.write(
        "La dificultad acaba traduciendose en un numero objetivo. Un hash valido tiene que ser menor que ese numero. "
        "Cuanto mas pequeño es el objetivo, menor es el espacio de hashes aceptables."
    )
    st.code(target_hex, language="text")
    st.write(
        f"El campo compacto `bits` del bloque es `{int(latest_block['bits'])}`. "
        f"Al expandirlo se obtiene un objetivo de 256 bits con aproximadamente `{int(snapshot['target_leading_zero_bits'])}` bits iniciales a cero."
    )

    clean_intervals = recent_blocks["minutes_since_prev"].dropna()
    if clean_intervals.empty:
        st.info("Todavia no hay suficientes bloques recientes para calcular intervalos.")
        return

    interval_col, stats_col = st.columns([2, 1])
    with interval_col:
        st.markdown("#### Como se estan espaciando los bloques")
        st.write(
            "Bitcoin apunta a 10 minutos de media, pero no promete 10 minutos exactos. "
            "Este histograma muestra si los ultimos bloques se han concentrado cerca del objetivo o si han tenido esperas muy dispersas."
        )
        interval_fig = px.histogram(
            recent_blocks.dropna(subset=["minutes_since_prev"]),
            x="minutes_since_prev",
            nbins=15,
            title="Distribucion del tiempo entre bloques recientes",
            labels={"minutes_since_prev": "Minutos entre bloques"},
        )
        interval_fig.update_traces(
            marker_color="#0B7285",
            marker_line_color="rgba(255,255,255,0.9)",
            marker_line_width=1.1,
            hovertemplate=(
                "<b>Intervalos agrupados</b><br>"
                "Minutos: %{x:.2f}<br>"
                "Bloques en el rango: %{y}"
                "<extra></extra>"
            ),
        )
        interval_fig.update_yaxes(title_text="Bloques")
        interval_fig.update_layout(bargap=0.08)
        st.plotly_chart(style_chart(interval_fig, height=420), width="stretch", config={"displayModeBar": False})

    with stats_col:
        st.markdown("#### Resumen temporal")
        st.metric("Media", f"{clean_intervals.mean():.2f} min")
        st.metric("Mediana", f"{clean_intervals.median():.2f} min")
        st.metric("Desviacion tipica", f"{clean_intervals.std(ddof=1):.2f} min")
        st.metric("Coef. variacion", f"{(clean_intervals.std(ddof=1) / clean_intervals.mean()):.2f}")
        st.info(
            "Los bloques suelen modelarse como un proceso aleatorio: lo normal no es una linea perfecta, sino una distribucion de esperas."
        )

    trend_df = recent_blocks.dropna(subset=["minutes_since_prev"]).copy()
    trend_df["timestamp_label"] = trend_df["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
    trend_fig = px.line(
        trend_df,
        x="timestamp_dt",
        y="minutes_since_prev",
        markers=True,
        title="Intervalos recientes a lo largo del tiempo",
        labels={
            "timestamp_dt": "Timestamp del bloque (UTC)",
            "minutes_since_prev": "Minutos desde el bloque anterior",
        },
        custom_data=["height", "timestamp_label", "minutes_since_prev"],
    )
    trend_fig.update_traces(
        line={"width": 2.8, "color": "#0B7285"},
        marker={"size": 8, "color": "#364FC7", "line": {"width": 1.6, "color": "#ffffff"}},
        hovertemplate=(
            "<b>Bloque %{customdata[0]:,}</b><br>"
            "Fecha: %{customdata[1]}<br>"
            "Intervalo: %{customdata[2]:.2f} min<br>"
            "Objetivo: 10.00 min"
            "<extra></extra>"
        ),
    )
    trend_fig.add_hline(
        y=10,
        line_dash="dash",
        line_color="#0B7285",
        annotation_text="Objetivo 10 min",
    )
    st.plotly_chart(style_chart(trend_fig, height=430), width="stretch", config={"displayModeBar": False})
    st.write(
        "Los puntos por encima de la linea tardaron mas de 10 minutos; los de debajo llegaron mas rapido. "
        "Una racha corta no es un problema: el ajuste de dificultad es el mecanismo que corrige desviaciones sostenidas."
    )

    st.markdown("#### Bloque usado como referencia")
    st.write(
        "Este resumen conecta las metricas con un bloque real. El hash y el campo `bits` son las piezas que se verifican con mas detalle en la seccion del bloque."
    )
    st.json(
        {
            "hash": latest_block["id"],
            "previous_block_hash": latest_block["previousblockhash"],
            "nonce": latest_block["nonce"],
            "bits": latest_block["bits"],
            "difficulty": latest_block["difficulty"],
            "timestamp": latest_block["timestamp"],
        }
    )

    avg_interval_seconds = clean_intervals.mean() * 60
    deviation_ratio = avg_interval_seconds / 600
    st.write(
        "Promedio observado en la muestra reciente: "
        f"`{avg_interval_seconds:.1f}` segundos por bloque, "
        f"es decir `{deviation_ratio:.2f}x` el objetivo ideal de 600 segundos."
    )

    if np.isfinite(deviation_ratio) and deviation_ratio > 1.25:
        takeaway(
            "La muestra reciente va lenta.",
            "El promedio reciente esta bastante por encima del objetivo. Si una situacion asi se mantuviera durante un periodo completo, la red tenderia a bajar la dificultad.",
            tone="warning",
        )
    elif np.isfinite(deviation_ratio) and deviation_ratio < 0.75:
        takeaway(
            "La muestra reciente va rapida.",
            "El promedio reciente esta bastante por debajo del objetivo. Si se mantuviera, la red tenderia a subir la dificultad.",
            tone="warning",
        )
    else:
        takeaway(
            "La muestra reciente esta cerca del objetivo.",
            "Aunque los bloques individuales varien, el promedio observado no se aleja demasiado de los 10 minutos por bloque.",
            tone="success",
        )
