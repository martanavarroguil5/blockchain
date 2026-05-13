from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from api.blockchain_client import BlockchainApiError, get_client
from modules.ui import concept_flow, module_header, story_panel, style_chart, styled_table, takeaway


TARGET_BLOCK_MINUTES = 10.0
DEFAULT_BLOCK_LIMIT = 240
MIN_MODEL_INTERVALS = 40
FEATURE_COLUMNS = [
    "minutes_since_prev",
    "absolute_target_deviation",
    "rolling_mean_12",
    "rolling_std_12",
    "rolling_z_score",
    "period_position",
    "negative_timestamp_jump",
]


@st.cache_data(ttl=300, show_spinner=False)
def load_anomaly_features(block_limit: int = DEFAULT_BLOCK_LIMIT) -> pd.DataFrame:
    client = get_client()
    recent_blocks = client.get_recent_blocks_window(limit=block_limit)
    blocks_df = pd.DataFrame(recent_blocks).sort_values("height").reset_index(drop=True)
    blocks_df["timestamp_dt"] = pd.to_datetime(blocks_df["timestamp"], unit="s", utc=True)
    blocks_df["minutes_since_prev"] = blocks_df["timestamp"].diff() / 60
    blocks_df = blocks_df.dropna(subset=["minutes_since_prev"]).copy()

    intervals = blocks_df["minutes_since_prev"]
    mean_interval = intervals.mean()
    std_interval = intervals.std(ddof=1)
    if std_interval == 0 or not np.isfinite(std_interval):
        blocks_df["z_score"] = 0.0
    else:
        blocks_df["z_score"] = (intervals - mean_interval) / std_interval

    rolling_mean = intervals.rolling(window=12, min_periods=3).mean()
    rolling_std = intervals.rolling(window=12, min_periods=3).std(ddof=1)
    expanding_mean = intervals.expanding(min_periods=1).mean()
    fallback_std = std_interval if np.isfinite(std_interval) and std_interval > 0 else 1.0

    blocks_df["absolute_target_deviation"] = (intervals - TARGET_BLOCK_MINUTES).abs()
    blocks_df["rolling_mean_12"] = rolling_mean.fillna(expanding_mean)
    blocks_df["rolling_std_12"] = rolling_std.replace(0, np.nan).fillna(fallback_std)
    blocks_df["rolling_z_score"] = (
        (intervals - blocks_df["rolling_mean_12"]) / blocks_df["rolling_std_12"]
    ).replace([np.inf, -np.inf], 0)
    blocks_df["period_position"] = (blocks_df["height"].astype(int) % 2016) / 2016
    blocks_df["negative_timestamp_jump"] = (intervals < 0).astype(int)
    blocks_df["baseline_anomaly"] = blocks_df["z_score"].abs() >= 2.5

    return blocks_df


def run_isolation_forest(blocks_df: pd.DataFrame, contamination: float) -> pd.DataFrame:
    try:
        from sklearn.ensemble import IsolationForest
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import RobustScaler
    except ImportError as exc:
        raise RuntimeError(
            "scikit-learn is required for the Isolation Forest model. Install the project requirements first."
        ) from exc

    model_df = blocks_df.copy()
    feature_frame = model_df[FEATURE_COLUMNS].replace([np.inf, -np.inf], np.nan)
    feature_frame = feature_frame.fillna(feature_frame.median(numeric_only=True)).fillna(0)

    model = make_pipeline(
        RobustScaler(),
        IsolationForest(
            n_estimators=250,
            contamination=contamination,
            random_state=42,
        ),
    )
    predictions = model.fit_predict(feature_frame)
    model_df["isolation_score"] = model.named_steps["isolationforest"].score_samples(
        model.named_steps["robustscaler"].transform(feature_frame)
    )
    model_df["model_anomaly"] = predictions == -1
    model_df["anomaly_label"] = np.where(
        model_df["model_anomaly"],
        "Anomalia Isolation Forest",
        np.where(model_df["baseline_anomaly"], "Solo z-score", "Normal"),
    )
    return model_df


def _format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_m4() -> None:
    module_header(
        "Anomalias con IA",
        "IA para detectar tiempos raros",
        "Un pipeline interpretable que convierte intervalos entre bloques en señales de investigacion.",
    )

    story_panel(
        "Que significa anomalia aqui",
        "Una anomalia no significa fraude ni bloque invalido.",
        "Significa que el intervalo temporal entre bloques se comporta de forma poco habitual respecto al contexto reciente y al objetivo de 10 minutos. "
        "El modelo sirve para priorizar revision: señala donde mirar primero, no dicta una sentencia.",
        [
            "El z-score marca valores extremos de forma simple y explicable.",
            "Isolation Forest combina varias señales para detectar rareza contextual.",
            "La evaluacion se centra en tasa de anomalias, solape con baseline y tabla de candidatos.",
        ],
    )
    concept_flow(
        [
            ("Datos", "Se toman bloques recientes y se calcula el tiempo desde el bloque anterior."),
            ("Features", "Se crean variables de desviacion, medias moviles, volatilidad local y posicion dentro del periodo de dificultad."),
            ("Baseline", "El z-score separa intervalos muy alejados de la media global."),
            ("Modelo", "Isolation Forest aprende que puntos son raros al compararlos con el resto de la muestra."),
        ]
    )

    block_limit = st.slider(
        "Muestra historica de bloques",
        min_value=80,
        max_value=400,
        value=DEFAULT_BLOCK_LIMIT,
        step=40,
        help="Valores mas altos dan mas contexto al modelo, pero requieren mas llamadas a fuentes publicas.",
    )
    contamination = st.slider(
        "Tasa esperada de anomalias",
        min_value=0.01,
        max_value=0.10,
        value=0.04,
        step=0.01,
        format="%.2f",
        help="Isolation Forest usa este valor como porcentaje aproximado de intervalos a marcar.",
    )

    try:
        blocks_df = load_anomaly_features(block_limit)
    except BlockchainApiError as exc:
        st.error(f"No se pudieron cargar datos publicos para el analisis de IA: {exc}")
        return
    except Exception as exc:
        st.error(f"Error inesperado preparando las variables de IA: {exc}")
        return

    if blocks_df.empty:
        st.info("Todavia no hay suficientes bloques para calcular variables de anomalia.")
        return

    if len(blocks_df) < MIN_MODEL_INTERVALS:
        st.info(f"Hacen falta al menos {MIN_MODEL_INTERVALS} intervalos para entrenar el modelo Isolation Forest.")
        return

    try:
        results_df = run_isolation_forest(blocks_df, contamination)
    except RuntimeError as exc:
        st.error(str(exc))
        return
    except Exception as exc:
        st.error(f"Error inesperado entrenando Isolation Forest: {exc}")
        return

    baseline_count = int(results_df["baseline_anomaly"].sum())
    model_count = int(results_df["model_anomaly"].sum())
    overlap_count = int((results_df["baseline_anomaly"] & results_df["model_anomaly"]).sum())
    anomaly_rate = model_count / len(results_df)

    metric_col_1, metric_col_2, metric_col_3, metric_col_4 = st.columns(4)
    metric_col_1.metric("Muestra del modelo", f"{len(results_df):,}")
    metric_col_2.metric("Intervalo medio", f"{results_df['minutes_since_prev'].mean():.2f} min")
    metric_col_3.metric("Anomalias IA", model_count, delta=_format_percent(anomaly_rate))
    metric_col_4.metric("Solape baseline", f"{overlap_count}/{max(baseline_count, 1)}")
    st.write(
        "El z-score detecta intervalos globalmente extremos. Isolation Forest añade contexto: mira varias variables a la vez y puede marcar un bloque "
        "porque su patron local es raro, aunque un unico numero no parezca escandaloso."
    )

    plot_df = results_df.copy()
    plot_df["block_hash_short"] = plot_df["id"].astype(str).str.slice(0, 6) + "..." + plot_df["id"].astype(str).str.slice(-6)
    plot_df["timestamp_label"] = plot_df["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
    plot_df["tooltip_label"] = plot_df["anomaly_label"].replace(
        {
            "Anomalia Isolation Forest": "Candidato IA",
            "Solo z-score": "Extremo estadistico",
        }
    )
    plot_df["tooltip_hint"] = np.select(
        [
            plot_df["model_anomaly"],
            plot_df["baseline_anomaly"],
        ],
        [
            "Prioridad alta para revisar",
            "Intervalo extremo por z-score",
        ],
        default="Comportamiento esperado",
    )

    fig = px.scatter(
        plot_df,
        x="timestamp_dt",
        y="minutes_since_prev",
        color="anomaly_label",
        size="absolute_target_deviation",
        color_discrete_map={
            "Normal": "#0B7285",
            "Solo z-score": "#E8590C",
            "Anomalia Isolation Forest": "#364FC7",
        },
        title="Intervalos entre bloques y anomalias detectadas",
        labels={
            "timestamp_dt": "Timestamp del bloque (UTC)",
            "minutes_since_prev": "Minutos desde el bloque anterior",
            "anomaly_label": "Clasificacion",
            "absolute_target_deviation": "Desviacion frente a 10 min",
        },
        custom_data=[
            "tooltip_label",
            "timestamp_label",
            "height",
            "absolute_target_deviation",
            "z_score",
            "rolling_z_score",
            "isolation_score",
            "block_hash_short",
            "tooltip_hint",
        ],
    )
    fig.update_traces(
        marker={
            "line": {"width": 1.6, "color": "rgba(255,255,255,0.92)"},
            "opacity": 0.86,
        },
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "%{customdata[8]}<br><br>"
            "Bloque %{customdata[2]:,}<br>"
            "%{customdata[1]}<br>"
            "Intervalo: <b>%{y:.2f} min</b><br>"
            "Desvio del objetivo: %{customdata[3]:.2f} min<br>"
            "z global / local: %{customdata[4]:.2f} / %{customdata[5]:.2f}<br>"
            "Score IA: %{customdata[6]:.4f}<br>"
            "Hash corto: %{customdata[7]}"
            "<extra></extra>"
        ),
    )
    fig.add_hline(
        y=TARGET_BLOCK_MINUTES,
        line_dash="dash",
        line_color="#0B7285",
        annotation_text="Objetivo 10 min",
    )
    st.plotly_chart(style_chart(fig, height=430), width="stretch", config={"displayModeBar": False})
    st.write(
        "Cada punto es el hueco temporal entre dos bloques consecutivos. Los puntos mas grandes se alejan mas del objetivo de 10 minutos. "
        "Los puntos marcados como anomalia son los candidatos que conviene revisar primero."
    )

    comparison_col, feature_col = st.columns([1, 1])
    with comparison_col:
        st.markdown("#### Evaluacion interpretable")
        st.write(
            "No existe una etiqueta oficial de 'anomalia real' para estos intervalos, asi que la evaluacion comprueba si el modelo se comporta con sentido: "
            "cuantos casos marca, cuanto coincide con el baseline y si detecta situaciones temporales llamativas."
        )
        styled_table(
            pd.DataFrame(
                [
                    ("Anomalias por z-score", baseline_count),
                    ("Anomalias por Isolation Forest", model_count),
                    ("Casos compartidos por ambos metodos", overlap_count),
                    ("Tasa de anomalias del modelo", _format_percent(anomaly_rate)),
                    ("Saltos temporales negativos marcados", int(results_df.loc[results_df["model_anomaly"], "negative_timestamp_jump"].sum())),
                ],
                columns=["Metrica", "Valor"],
            )
        )

    with feature_col:
        st.markdown("#### Variables que usa el modelo")
        styled_table(
            pd.DataFrame(
                [
                    ("minutes_since_prev", "Intervalo observado entre bloques consecutivos"),
                    ("absolute_target_deviation", "Distancia frente al objetivo de 10 minutos"),
                    ("rolling_mean_12", "Contexto local de tiempos recientes"),
                    ("rolling_std_12", "Volatilidad local de los intervalos"),
                    ("rolling_z_score", "Sorpresa estandarizada en el contexto cercano"),
                    ("period_position", "Posicion dentro del periodo de ajuste de 2016 bloques"),
                    ("negative_timestamp_jump", "El timestamp del header retrocede"),
                ],
                columns=["Variable", "Significado"],
            )
        )

    st.markdown("#### Candidatos prioritarios")
    st.write(
        "La tabla se ordena por `isolation_score`. Cuanto menor es el score, mas raro le parece el caso al modelo; por eso las primeras filas son las mas interesantes."
    )
    anomaly_table = results_df.loc[results_df["model_anomaly"]].copy()
    if anomaly_table.empty:
        st.success("La muestra actual no ha producido candidatos de anomalia.")
    else:
        anomaly_table = anomaly_table.sort_values("isolation_score").head(12)
        anomaly_table["timestamp_dt"] = anomaly_table["timestamp_dt"].dt.strftime("%Y-%m-%d %H:%M UTC")
        anomaly_table["hash_corto"] = anomaly_table["id"].astype(str).str.slice(0, 6) + "..." + anomaly_table["id"].astype(str).str.slice(-6)
        anomaly_table["minutes_since_prev"] = anomaly_table["minutes_since_prev"].map(lambda value: f"{float(value):.2f} min")
        anomaly_table["z_score"] = anomaly_table["z_score"].map(lambda value: f"{float(value):.2f}")
        anomaly_table["rolling_z_score"] = anomaly_table["rolling_z_score"].map(lambda value: f"{float(value):.2f}")
        anomaly_table["isolation_score"] = anomaly_table["isolation_score"].map(lambda value: f"{float(value):.4f}")
        styled_table(
            anomaly_table.rename(
                columns={
                    "height": "Bloque",
                    "timestamp_dt": "Fecha",
                    "minutes_since_prev": "Intervalo",
                    "z_score": "z-score",
                    "rolling_z_score": "z-score local",
                    "isolation_score": "Score IA",
                    "hash_corto": "Hash corto",
                }
            )[
                [
                    "Bloque",
                    "Fecha",
                    "Intervalo",
                    "z-score",
                    "z-score local",
                    "Score IA",
                    "Hash corto",
                ]
            ]
        )

    st.markdown("#### Resultado del modelo")
    styled_table(
        pd.DataFrame(
            [
                ("Datos", "Timestamps recientes de bloques Bitcoin con Blockstream y fallback a Mempool.space"),
                ("Baseline", "Umbral z-score global de 2.5 desviaciones tipicas"),
                ("Modelo", "Isolation Forest con variables temporales escaladas de forma robusta"),
                ("Evaluacion", "Tasa de anomalias, solape con colas estadisticas y ranking de candidatos"),
                ("Limitacion", "Sin etiquetas reales, el resultado es descubrimiento de anomalias, no accuracy supervisada"),
            ],
            columns=["Area", "Implementacion"],
        )
    )

    if overlap_count > 0:
        takeaway(
            "El modelo esta funcionando y coincide parcialmente con el baseline.",
            "Ese solape ayuda a explicar el resultado: algunos candidatos son extremos tambien con una regla estadistica simple.",
            tone="success",
        )
    else:
        takeaway(
            "El modelo esta funcionando, pero detecta rareza contextual.",
            "En esta muestra Isolation Forest no coincide con el z-score global. Eso puede pasar cuando lo raro no es un valor aislado, sino la combinacion de contexto y timing.",
            tone="warning",
        )
