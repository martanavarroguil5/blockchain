from __future__ import annotations

import streamlit as st
import pandas as pd

from modules.m1_pow_monitor import render_m1
from modules.m2_block_header import render_m2
from modules.m3_difficulty_history import render_m3
from modules.m4_ai_anomaly import render_m4
from modules.ui import apply_app_theme, concept_flow, hero, insight_grid, story_panel, styled_table, takeaway


st.set_page_config(
    page_title="ProofLab Bitcoin",
    page_icon="C",
    layout="wide",
)

apply_app_theme()
hero()

with st.sidebar:
    st.header("ProofLab Bitcoin")
    st.markdown("**Autora:** Marta Navarro")
    st.markdown("**Tema:** prueba de trabajo en Bitcoin")
    st.divider()
    st.markdown("**Ruta de lectura**")
    st.markdown("1. Red en directo")
    st.markdown("2. Bloque por dentro")
    st.markdown("3. Dificultad")
    st.markdown("4. Anomalias con IA")
    st.info("Cada apartado parte de datos reales y explica como interpretar lo que se ve.")

selected_page = st.radio(
    "Seccion",
    [
        "Mapa",
        "Red en directo",
        "Bloque por dentro",
        "Dificultad",
        "Anomalias con IA",
    ],
    horizontal=True,
    label_visibility="collapsed",
)

if selected_page == "Mapa":
    st.subheader("Mapa de lectura")
    story_panel(
        "Conceptos base",
        "Antes de mirar datos, hay que saber que piezas forman Bitcoin.",
        "Bitcoin es un registro publico de transacciones. Las transacciones se agrupan en bloques, "
        "cada bloque se enlaza con el anterior y asi se forma la cadena de bloques. Para añadir un bloque, "
        "los mineros prueban muchos hashes. La regla que tienen que cumplir es concreta: el hash del bloque, interpretado como numero, "
        "debe ser menor que un numero objetivo. La dificultad no es ese objetivo, sino una forma de decir cuanto se ha endurecido: "
        "si marca 134 T, encontrar un hash valido es unas 134 billones de veces mas dificil que en el nivel base.",
        [
            "Bloque: paquete de transacciones aceptado como una nueva pagina del historial.",
            "Cadena: sucesion de bloques enlazados; cada bloque depende criptograficamente del anterior.",
            "Hash: huella numerica del bloque; si cambia el bloque, cambia el hash.",
            "Mineros: ordenadores que prueban hashes para proponer el siguiente bloque.",
            "Dificultad: escala que endurece el objetivo del hash; cuanto mas alta, menos hashes cumplen la regla.",
            "Altura: posicion de un bloque dentro de la cadena.",
        ],
    )
    story_panel(
        "Idea central",
        "La app explica como Bitcoin decide que un bloque es valido.",
        "La idea es seguir el camino completo: primero ver que esta pasando ahora en la red, "
        "despues mirar un bloque real por dentro, comprobar su hash y entender por que la dificultad cambia con el tiempo. "
        "Al final se usan datos recientes para detectar intervalos entre bloques que se salen de lo habitual.",
        [
            "Red en directo: muestra el ultimo bloque, la dificultad, el hash rate y las transacciones.",
            "Bloque por dentro: enseña los datos tecnicos del bloque y recalcula su hash.",
            "Dificultad: explica como Bitcoin intenta mantener un ritmo medio de 10 minutos por bloque.",
            "Anomalias con IA: busca bloques cuyo tiempo de aparicion fue raro comparado con el contexto reciente.",
        ],
    )
    insight_grid(
        [
            ("Bloque real", "Datos live", "La informacion viene de exploradores publicos de Bitcoin."),
            ("Prueba local", "SHA-256 x2", "El hash del header se recalcula desde cero."),
            ("Ritmo esperado", "10 min", "La dificultad intenta mantener ese promedio a largo plazo."),
            ("IA", "Isolation Forest", "El modelo destaca patrones temporales poco habituales."),
        ]
    )
    st.markdown("#### Recorrido")
    concept_flow(
        [
            (
                "Observar",
                "Se muestra el ultimo bloque, la dificultad, la potencia estimada y si los bloques recientes estan llegando rapido o lento.",
            ),
            (
                "Verificar",
                "Se descarga el bloque crudo, se separa el header de 80 bytes y se comprueba que el hash cumple la regla de Proof of Work.",
            ),
            (
                "Contextualizar",
                "Se ve que la dificultad no es fija: cambia cada 2016 bloques para compensar la potencia minera.",
            ),
            (
                "Investigar",
                "Los tiempos entre bloques se convierten en variables y un modelo no supervisado señala casos raros.",
            ),
        ]
    )
    st.markdown("#### Que se aprende en cada parte")
    styled_table(
        pd.DataFrame(
            {
            "Parte": ["Red en directo", "Bloque por dentro", "Dificultad", "Anomalias con IA"],
            "Pregunta principal": [
                "Que esta pasando ahora en la red Bitcoin?",
                "Como se comprueba que un bloque hizo trabajo real?",
                "Por que la dificultad sube o baja con el tiempo?",
                "Que intervalos entre bloques son raros y merecen revision?",
            ],
            "Idea clave": [
                "El coste de minar se observa con dificultad, hash rate e intervalos.",
                "Un bloque se puede verificar recalculando su hash.",
                "El protocolo corrige el ritmo sin una autoridad central.",
                "La IA ayuda a priorizar patrones temporales poco comunes.",
            ],
            }
        )
    )
    takeaway(
        "Lo importante no es memorizar los numeros.",
        "Lo importante es entender la cadena de razonamiento: datos reales, verificacion local, mecanismo de ajuste y analisis de patrones. "
        "Esa es la diferencia entre enseñar datos sueltos y explicar Bitcoin.",
        tone="success",
    )

elif selected_page == "Red en directo":
    render_m1()

elif selected_page == "Bloque por dentro":
    render_m2()

elif selected_page == "Dificultad":
    render_m3()

elif selected_page == "Anomalias con IA":
    render_m4()
