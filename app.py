from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"

COLORES = {
    "azul": "#214E66",
    "turquesa": "#2A7F8E",
    "ocre": "#D7A84B",
    "coral": "#C96B4B",
    "verde": "#6C7A59",
    "gris": "#7C8991",
    "fondo": "#F7F6F2",
}

MESES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}


@st.cache_data
def cargar_datos() -> tuple[pd.DataFrame, ...]:
    mensual = pd.read_csv(DATA_DIR / "serie_mensual_total.csv", parse_dates=["fecha"])
    vias = pd.read_csv(DATA_DIR / "serie_mensual_por_via.csv", parse_dates=["fecha"])
    estacional = pd.read_csv(DATA_DIR / "indice_estacional.csv")
    modelos = pd.read_csv(DATA_DIR / "metricas_modelos_serie_total.csv")
    pred_lstm = pd.read_csv(DATA_DIR / "predicciones_lstm.csv", parse_dates=["fecha"])
    metricas_lstm = pd.read_csv(DATA_DIR / "metricas_lstm.csv")
    return mensual, vias, estacional, modelos, pred_lstm, metricas_lstm


def fecha_larga(fecha: pd.Timestamp) -> str:
    return f"{MESES[int(fecha.month)]} de {int(fecha.year)}"


def fecha_corta(fecha: pd.Timestamp) -> str:
    mes = MESES[int(fecha.month)][:3].capitalize()
    return f"{mes}. {int(fecha.year)}"


def abreviar_cantidad(valor: float) -> str:
    if abs(valor) >= 1_000_000:
        return f"{valor / 1_000_000:,.1f} millones"
    if abs(valor) >= 1_000:
        return f"{valor / 1_000:,.0f} mil"
    return f"{valor:,.0f}"


st.set_page_config(
    page_title="Observatorio del flujo turístico a Guatemala",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .stApp {background-color: #F7F6F2; color: #1E1E1E;}
    h1, h2, h3 {color: #214E66;}
    [data-testid="stSidebar"] {background-color: #ECE9E1;}
    [data-testid="stMetric"] {background: #FFFFFF; border: 1px solid #D9D9D9;
        border-radius: 0.35rem; padding: 0.8rem;}
    .nota {font-size: 0.92rem; color: #4D4D4D;}
    </style>
    """,
    unsafe_allow_html=True,
)

mensual, vias, estacional, modelos, pred_lstm, metricas_lstm = cargar_datos()
anio_min = int(mensual.fecha.dt.year.min())
anio_max = int(mensual.fecha.dt.year.max())

with st.sidebar:
    st.header("Controles")
    anios = st.slider(
        "Periodo de consulta",
        min_value=anio_min,
        max_value=anio_max,
        value=(anio_min, anio_max),
    )
    mostrar_promedio = st.checkbox("Mostrar promedio mensual del periodo", value=True)
    st.caption(
        "Fuente académica consolidada con respaldos históricos, IGM e INGUAT. "
        "El filtro turístico suma turistas y excursionistas."
    )
    if anios[1] == 2026:
        st.warning("2026 contiene únicamente información de enero a junio.")

filtro = mensual[mensual.fecha.dt.year.between(anios[0], anios[1])].copy()
filtro_vias = vias[vias.fecha.dt.year.between(anios[0], anios[1])].copy()

st.title("Observatorio del flujo turístico a Guatemala")
st.write(
    "El tablero resume el ingreso mensual de turistas y excursionistas. "
    "Seleccione un punto de la serie histórica para consultar cómo se distribuyó "
    "ese mes entre las vías aérea, marítima y terrestre."
)

if filtro.empty:
    st.warning("No hay datos para el periodo seleccionado.")
    st.stop()

total_periodo = float(filtro.viajeros.sum())
columnas_via = ["Aérea", "Marítima", "Terrestre"]
total_vias = float(filtro_vias[columnas_via].sum().sum())
participacion_terrestre = (
    float(filtro_vias["Terrestre"].sum()) / total_vias if total_vias else 0.0
)
fila_pico = filtro.loc[filtro.viajeros.idxmax()]
promedio = float(filtro.viajeros.mean())

k1, k2, k3, k4 = st.columns(4)
k1.metric("Visitantes del periodo", abreviar_cantidad(total_periodo))
k2.metric("Participación terrestre", f"{participacion_terrestre:.1%}")
k3.metric("Mes con mayor flujo", fecha_corta(fila_pico.fecha))
k4.metric("Promedio mensual", abreviar_cantidad(promedio))

tab_exploracion, tab_modelos, tab_metodologia = st.tabs(
    ["Exploración", "Estacionalidad y modelos", "Metodología"]
)

with tab_exploracion:
    st.subheader("Evolución mensual de visitantes")
    fig_serie = go.Figure()
    fig_serie.add_trace(
        go.Scatter(
            x=filtro.fecha,
            y=filtro.viajeros,
            mode="lines+markers",
            name="Turistas y excursionistas",
            line={"color": COLORES["azul"], "width": 2.5},
            marker={"size": 5, "opacity": 0.65},
            customdata=filtro.fecha.dt.strftime("%Y-%m-%d").to_numpy().reshape(-1, 1),
            hovertemplate="<b>%{x|%B %Y}</b><br>Visitantes: %{y:,.0f}<extra></extra>",
        )
    )
    if mostrar_promedio:
        fig_serie.add_hline(
            y=promedio,
            line_dash="dash",
            line_color=COLORES["ocre"],
            annotation_text=f"Promedio: {promedio:,.0f}",
            annotation_position="top left",
        )
    fig_serie.add_vrect(
        x0="2020-03-01",
        x1="2021-12-31",
        fillcolor=COLORES["coral"],
        opacity=0.10,
        line_width=0,
        annotation_text="Periodo atípico 2020–2021",
        annotation_position="top left",
    )
    fig_serie.update_layout(
        height=450,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        xaxis_title="Mes",
        yaxis_title="Visitantes",
        hovermode="x",
        paper_bgcolor=COLORES["fondo"],
        plot_bgcolor="#FFFFFF",
        font={"color": "#1E1E1E"},
        showlegend=False,
    )
    fig_serie.update_xaxes(rangeslider={"visible": True}, gridcolor="#EEEEEE")
    fig_serie.update_yaxes(tickformat=",.0f", gridcolor="#D9D9D9")

    evento = st.plotly_chart(
        fig_serie,
        use_container_width=True,
        key="serie_turismo",
        on_select="rerun",
        selection_mode="points",
        config={"displaylogo": False},
    )

    fecha_seleccionada = pd.Timestamp(filtro.fecha.max())
    if evento and evento.selection and evento.selection.points:
        punto = evento.selection.points[0]
        customdata = punto.get("customdata")
        if customdata:
            fecha_seleccionada = pd.Timestamp(customdata[0])

    detalle = vias[vias.fecha == fecha_seleccionada]
    st.subheader(f"Vía de ingreso en {fecha_larga(fecha_seleccionada)}")
    if detalle.empty:
        st.info("No hay desglose por vía para el mes seleccionado.")
    else:
        valores = detalle.iloc[0][columnas_via].astype(float)
        colores_via = [COLORES["azul"], COLORES["turquesa"], COLORES["ocre"]]
        fig_vias = go.Figure(
            go.Bar(
                x=columnas_via,
                y=valores.values,
                marker_color=colores_via,
                text=[f"{v:,.0f}" for v in valores.values],
                textposition="outside",
                hovertemplate="<b>%{x}</b><br>Visitantes: %{y:,.0f}<extra></extra>",
            )
        )
        fig_vias.update_layout(
            height=370,
            margin={"l": 10, "r": 10, "t": 25, "b": 10},
            xaxis_title="Vía de ingreso",
            yaxis_title="Visitantes",
            paper_bgcolor=COLORES["fondo"],
            plot_bgcolor="#FFFFFF",
            font={"color": "#1E1E1E"},
        )
        fig_vias.update_yaxes(tickformat=",.0f", gridcolor="#D9D9D9")
        st.plotly_chart(
            fig_vias,
            use_container_width=True,
            config={"displaylogo": False},
        )
        total_mes = float(valores.sum())
        principal = valores.idxmax()
        st.caption(
            f"Selección actual: {fecha_larga(fecha_seleccionada)}. "
            f"Total: {total_mes:,.0f} visitantes. La vía con mayor volumen fue "
            f"{principal.lower()} ({valores[principal] / total_mes:.1%})."
        )

with tab_modelos:
    izquierda, derecha = st.columns(2)

    with izquierda:
        st.subheader("Patrón estacional previo a 2020")
        colores_est = [
            COLORES["ocre"] if valor >= 120 else COLORES["turquesa"]
            for valor in estacional.indice_estacional
        ]
        fig_estacional = go.Figure(
            go.Bar(
                x=estacional.mes,
                y=estacional.indice_estacional,
                marker_color=colores_est,
                hovertemplate="<b>%{x}</b><br>Índice: %{y:.1f}<extra></extra>",
            )
        )
        fig_estacional.add_hline(
            y=100,
            line_dash="dash",
            line_color=COLORES["gris"],
            annotation_text="Promedio = 100",
        )
        fig_estacional.update_layout(
            height=380,
            margin={"l": 10, "r": 10, "t": 20, "b": 10},
            xaxis_title="Mes",
            yaxis_title="Índice estacional",
            paper_bgcolor=COLORES["fondo"],
            plot_bgcolor="#FFFFFF",
            font={"color": "#1E1E1E"},
        )
        fig_estacional.update_yaxes(gridcolor="#D9D9D9")
        st.plotly_chart(fig_estacional, use_container_width=True, config={"displaylogo": False})

    with derecha:
        st.subheader("Desempeño de modelos del Laboratorio 1")
        orden_modelos = modelos.sort_values("rmse", ascending=False)
        mejor = modelos.loc[modelos.rmse.idxmin(), "modelo"]
        colores_modelos = [
            COLORES["ocre"] if modelo == mejor else COLORES["gris"]
            for modelo in orden_modelos.modelo
        ]
        fig_modelos = go.Figure(
            go.Bar(
                x=orden_modelos.rmse,
                y=orden_modelos.modelo,
                orientation="h",
                marker_color=colores_modelos,
                customdata=orden_modelos[["mae"]].to_numpy(),
                hovertemplate=(
                    "<b>%{y}</b><br>RMSE: %{x:,.0f}<br>"
                    "MAE: %{customdata[0]:,.0f}<extra></extra>"
                ),
            )
        )
        fig_modelos.update_layout(
            height=380,
            margin={"l": 10, "r": 10, "t": 20, "b": 10},
            xaxis_title="RMSE en prueba (menor es mejor)",
            yaxis_title="",
            paper_bgcolor=COLORES["fondo"],
            plot_bgcolor="#FFFFFF",
            font={"color": "#1E1E1E"},
        )
        fig_modelos.update_xaxes(tickformat=",.0f", gridcolor="#D9D9D9")
        st.plotly_chart(fig_modelos, use_container_width=True, config={"displaylogo": False})
        st.caption(f"Entre estos cinco modelos, {mejor} obtuvo el RMSE más bajo.")

    st.subheader("Predicción LSTM del Laboratorio 2")
    opciones_lstm = dict(
        pred_lstm[["serie", "clave"]].drop_duplicates().itertuples(index=False, name=None)
    )
    serie_lstm = st.selectbox("Serie modelada", options=list(opciones_lstm))
    clave_lstm = opciones_lstm[serie_lstm]
    parte_lstm = pred_lstm[pred_lstm.clave == clave_lstm].sort_values("fecha")
    fig_lstm = go.Figure()
    fig_lstm.add_trace(
        go.Scatter(
            x=parte_lstm.fecha,
            y=parte_lstm.real,
            mode="lines",
            name="Valor observado",
            line={"color": COLORES["azul"], "width": 2.5},
        )
    )
    fig_lstm.add_trace(
        go.Scatter(
            x=parte_lstm.fecha,
            y=parte_lstm.prediccion,
            mode="lines",
            name="Predicción LSTM",
            line={"color": COLORES["coral"], "width": 2.2, "dash": "dash"},
        )
    )
    fig_lstm.update_layout(
        height=410,
        margin={"l": 10, "r": 10, "t": 20, "b": 10},
        xaxis_title="Mes",
        yaxis_title="Visitantes",
        hovermode="x unified",
        paper_bgcolor=COLORES["fondo"],
        plot_bgcolor="#FFFFFF",
        font={"color": "#1E1E1E"},
        legend={"orientation": "h", "y": 1.1},
    )
    fig_lstm.update_yaxes(tickformat=",.0f", gridcolor="#D9D9D9")
    st.plotly_chart(fig_lstm, use_container_width=True, config={"displaylogo": False})
    metrica = metricas_lstm[metricas_lstm.clave == clave_lstm]
    if not metrica.empty:
        fila = metrica.iloc[0]
        st.caption(
            f"Modelo LSTM seleccionado: {fila.configuracion}. "
            f"MAE = {fila.mae_test:,.0f}, RMSE = {fila.rmse_test:,.0f} y "
            f"sMAPE = {fila.smape_test:.1f}%."
        )

with tab_metodologia:
    st.subheader("Fuente y definiciones")
    st.write(
        "La base reúne ingresos de viajeros internacionales a Guatemala entre enero "
        "de 2009 y junio de 2026. Para este tablero se suman únicamente las categorías "
        "Turista y Excursionista. La categoría Viajero no se incluye porque agrupa "
        "cruces fronterizos que no necesariamente corresponden a visitantes."
    )
    st.subheader("Limitaciones de interpretación")
    st.markdown(
        """
        - La base es de uso académico y no debe presentarse como una publicación oficial.
        - Desde 2023 cambian la metodología y el nivel de detalle por país.
        - La vía marítima pierde detalle desde 2017.
        - El periodo 2020–2021 es atípico y no representa el patrón turístico habitual.
        - Los valores decimales provienen de estimaciones expandidas de encuesta.
        - El año 2026 contiene únicamente seis meses y no debe compararse como año completo.
        """
    )
    st.caption(
        "Las métricas de modelos clásicos y LSTM se muestran por separado porque "
        "provienen de ejercicios con configuraciones y evaluaciones distintas."
    )
