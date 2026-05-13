from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.bitcoin_math import human_difficulty
from modules.ui import concept_flow, module_header, story_panel, style_chart, styled_table, takeaway


BLOCKS_PER_ADJUSTMENT = 2016
TARGET_SECONDS_PER_BLOCK = 600


def _period_bounds(latest_height: int, periods: int) -> list[tuple[int, int, int]]:
    latest_completed_period = latest_height // BLOCKS_PER_ADJUSTMENT - 1
    first_period = max(0, latest_completed_period - periods + 1)
    return [
        (
            period_index,
            period_index * BLOCKS_PER_ADJUSTMENT,
            (period_index + 1) * BLOCKS_PER_ADJUSTMENT,
        )
        for period_index in range(first_period, latest_completed_period + 1)
    ]


@st.cache_data(ttl=600, show_spinner=False)
def load_difficulty_periods(periods: int = 8) -> pd.DataFrame:
    client = get_client()
    latest_block = client.get_latest_block()
    latest_height = int(latest_block["height"])

    rows: list[dict[str, object]] = []
    for period_index, start_height, next_start_height in _period_bounds(latest_height, periods):
        start_block = client.get_block_by_height(start_height)
        next_period_block = client.get_block_by_height(next_start_height)
        elapsed_seconds = int(next_period_block["timestamp"]) - int(start_block["timestamp"])
        expected_seconds = BLOCKS_PER_ADJUSTMENT * TARGET_SECONDS_PER_BLOCK

        rows.append(
            {
                "period_index": period_index,
                "start_height": start_height,
                "next_adjustment_height": next_start_height,
                "period_start": datetime.fromtimestamp(int(start_block["timestamp"]), UTC),
                "difficulty": float(start_block["difficulty"]),
                "actual_days": elapsed_seconds / 86_400,
                "target_days": expected_seconds / 86_400,
                "actual_vs_target_ratio": elapsed_seconds / expected_seconds,
                "average_block_minutes": elapsed_seconds / BLOCKS_PER_ADJUSTMENT / 60,
            }
        )

    return pd.DataFrame(rows)


def render_m3() -> None:
    module_header(
        "Dificultad",
        "La dificultad como piloto automatico",
        "Periodos recientes de ajuste y comparacion entre tiempo real y objetivo de 10 minutos.",
    )
    story_panel(
        "El problema que resuelve",
        "Bitcoin necesita que los bloques no salgan ni demasiado rapido ni demasiado lento.",
        "Como la potencia minera cambia constantemente, la red no puede fijar una dificultad para siempre. "
        "Cada 2016 bloques compara el tiempo real con el tiempo esperado y ajusta la dificultad para volver al ritmo de 10 minutos por bloque.",
        [
            "Si los bloques llegan demasiado rapido, la dificultad tiende a subir.",
            "Si llegan demasiado lento, la dificultad tiende a bajar.",
            "El ajuste no reacciona a un bloque aislado, sino a un periodo completo.",
        ],
    )
    concept_flow(
        [
            (
                "Elegir muestra",
                "Se decide cuantos periodos completos de ajuste mirar. Cada periodo tiene 2016 bloques, unas dos semanas.",
            ),
            (
                "Medir tiempo",
                "Para cada periodo se consulta el bloque inicial y el bloque del siguiente ajuste, y se calcula cuanto tardo realmente.",
            ),
            (
                "Comparar",
                "Ese tiempo real se compara con el objetivo teorico: 2016 bloques por 10 minutos cada uno.",
            ),
            (
                "Interpretar",
                "Si el periodo fue rapido, la dificultad tiende a subir; si fue lento, tiende a bajar.",
            ),
        ]
    )

    control_col, context_col = st.columns([1, 2.2])
    with control_col:
        period_count = st.selectbox(
            "Periodos analizados",
            [4, 6, 8, 10, 12],
            index=2,
            format_func=lambda value: f"{value} periodos",
            help="Mas periodos dan mas contexto historico, pero requieren mas llamadas a las APIs publicas.",
        )
    with context_col:
        st.markdown("#### Que cambia este selector")
        st.write(
            "Cada periodo contiene 2016 bloques. Si eliges mas periodos, la grafica mira mas historial; "
            "si eliges menos, se centra en los ajustes mas recientes. Al cambiarlo se vuelven a consultar datos publicos."
        )

    try:
        with st.spinner("Consultando bloques de inicio y fin de cada periodo..."):
            periods_df = load_difficulty_periods(period_count)
    except BlockchainApiError as exc:
        st.error(f"No se pudo cargar el historial de dificultad desde las fuentes publicas: {exc}")
        return
    except Exception as exc:
        st.error(f"Error inesperado al preparar el historial de dificultad: {exc}")
        return

    if periods_df.empty:
        st.info("No hay periodos completos de ajuste disponibles en la respuesta actual.")
        return

    latest_row = periods_df.iloc[-1]
    metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
    metric_col_1.metric("Ultimo periodo completo", f"{int(latest_row['period_index']):,}")
    metric_col_2.metric("Dificultad del periodo", human_difficulty(float(latest_row["difficulty"])))
    metric_col_3.metric(
        "Media por bloque",
        f"{float(latest_row['average_block_minutes']):.2f} min",
        delta=f"{(float(latest_row['actual_vs_target_ratio']) - 1) * 100:+.1f}% vs objetivo",
    )

    chart_df = periods_df.copy()
    chart_df["difficulty_label"] = chart_df["difficulty"].map(lambda value: human_difficulty(float(value)))
    chart_df["period_start_label"] = chart_df["period_start"].dt.strftime("%Y-%m-%d")

    difficulty_fig = px.line(
        chart_df,
        x="period_start",
        y="difficulty",
        markers=True,
        title="Dificultad de Bitcoin en cada evento de ajuste",
        labels={
            "period_start": "Fecha del ajuste (UTC)",
            "difficulty": "Dificultad",
        },
        custom_data=["period_index", "period_start_label", "difficulty_label", "average_block_minutes"],
    )
    difficulty_fig.update_traces(
        line={"width": 3, "color": "#0B7285"},
        marker={"size": 10, "color": "#364FC7", "line": {"width": 2, "color": "#ffffff"}},
        hovertemplate=(
            "<b>Ajuste %{customdata[0]:,}</b><br>"
            "Fecha: %{customdata[1]}<br>"
            "Dificultad: %{customdata[2]}<br>"
            "Media por bloque: %{customdata[3]:.2f} min"
            "<extra></extra>"
        ),
    )
    for row in periods_df.itertuples():
        difficulty_fig.add_vline(x=row.period_start, line_dash="dot", line_color="rgba(80,80,80,0.35)")
    st.markdown("#### Grafica 1: como cambia la dificultad")
    st.write(
        "Cada punto representa la dificultad vigente al inicio de un periodo de 2016 bloques. "
        "La linea sube cuando Bitcoin endurece la busqueda de hashes validos y baja cuando la suaviza. "
        "Las lineas verticales marcan los eventos de ajuste."
    )
    st.plotly_chart(style_chart(difficulty_fig, height=430), width="stretch", config={"displayModeBar": False})

    ratio_fig = px.bar(
        chart_df,
        x="period_start",
        y="actual_vs_target_ratio",
        title="Duracion real del periodo frente al objetivo",
        labels={
            "period_start": "Inicio del periodo (UTC)",
            "actual_vs_target_ratio": "Duracion real / objetivo",
        },
        custom_data=[
            "period_index",
            "period_start_label",
            "start_height",
            "next_adjustment_height",
            "average_block_minutes",
            "actual_days",
            "target_days",
        ],
    )
    ratio_fig.update_traces(
        marker_color="#0B7285",
        marker_line_color="rgba(255,255,255,0.9)",
        marker_line_width=1.2,
        hovertemplate=(
            "<b>Periodo %{customdata[0]:,}</b><br>"
            "Inicio: %{customdata[1]}<br>"
            "Alturas: %{customdata[2]:,} a %{customdata[3]:,}<br>"
            "Ratio real/objetivo: %{y:.3f}<br>"
            "Media por bloque: %{customdata[4]:.2f} min<br>"
            "Duracion real: %{customdata[5]:.2f} dias<br>"
            "Objetivo: %{customdata[6]:.2f} dias"
            "<extra></extra>"
        ),
    )
    ratio_fig.add_hline(
        y=1,
        line_dash="dash",
        line_color="#0B7285",
        annotation_text="Objetivo",
    )
    st.markdown("#### Grafica 2: si los bloques fueron rapidos o lentos")
    st.write(
        "Esta grafica calcula la duracion real de cada periodo y la divide entre la duracion esperada. "
        "El valor ideal es 1: significa que el periodo duro lo esperado. Por debajo de 1, los bloques llegaron mas rapido; "
        "por encima de 1, llegaron mas lento."
    )
    st.plotly_chart(style_chart(ratio_fig, height=420), width="stretch", config={"displayModeBar": False})

    st.markdown("#### Tabla auditada de periodos")
    st.write(
        "Cada fila representa un periodo completo de 2016 bloques. Asi se puede revisar de donde salen las graficas: altura inicial, siguiente ajuste y tiempo medio por bloque."
    )
    display_df = periods_df.copy()
    display_df["Fecha"] = display_df["period_start"].dt.strftime("%Y-%m-%d")
    display_df["Dificultad"] = display_df["difficulty"].map(lambda value: human_difficulty(float(value)))
    display_df["Media por bloque"] = display_df["average_block_minutes"].map(lambda value: f"{float(value):.2f} min")
    display_df["Ratio real/objetivo"] = display_df["actual_vs_target_ratio"].map(lambda value: f"{float(value):.3f}")
    styled_table(
        display_df.rename(
            columns={
                "period_index": "Periodo",
                "start_height": "Altura inicial",
                "next_adjustment_height": "Siguiente ajuste",
            }
        )[
            [
                "Periodo",
                "Altura inicial",
                "Siguiente ajuste",
                "Fecha",
                "Dificultad",
                "Media por bloque",
                "Ratio real/objetivo",
            ]
        ]
    )

    st.info(
        "Regla de lectura: ratio menor que 1 significa que el periodo fue mas rapido que el calendario teorico; ratio mayor que 1 significa que fue mas lento."
    )

    latest_ratio = float(latest_row["actual_vs_target_ratio"])
    if latest_ratio < 0.98:
        takeaway(
            "El ultimo periodo fue mas rapido que el objetivo.",
            "Eso apunta a que la potencia minera efectiva fue alta durante ese periodo. La respuesta esperada del protocolo es endurecer la dificultad.",
            tone="warning",
        )
    elif latest_ratio > 1.02:
        takeaway(
            "El ultimo periodo fue mas lento que el objetivo.",
            "Eso apunta a que la potencia minera efectiva fue menor o menos eficiente. La respuesta esperada es suavizar la dificultad.",
            tone="warning",
        )
    else:
        takeaway(
            "El ultimo periodo quedo cerca del calendario teorico.",
            "La duracion real esta bastante alineada con el objetivo de dos semanas por cada 2016 bloques.",
            tone="success",
        )
