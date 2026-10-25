from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.analisis import agregar, fecha_del_evento, ranking
from src.preparar_datos import preparar, VIAS

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed"
C = {"azul":"#214E66", "turquesa":"#2A7F8E", "ocre":"#D7A84B", "coral":"#C96B4B", "verde":"#6C7A59", "gris":"#7C8991"}
COLORES_VIA = {"Aérea":C["azul"], "Marítima":C["turquesa"], "Terrestre":C["verde"]}
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
VISTAS = ["Evolución", "Vías", "Mercados", "Regiones", "Fronteras", "Estacionalidad", "Modelos", "Predicción LSTM"]


@st.cache_data
def cargar():
    if not (DATA/"auditoria.json").exists():
        preparar()
    nombres = ["serie_mensual_total", "serie_mensual_por_via", "mercados", "regiones", "fronteras", "predicciones_lstm"]
    datos = {n:pd.read_csv(DATA/f"{n}.csv", parse_dates=["fecha"]) for n in nombres}
    for n in ["indice_estacional", "metricas_modelos", "metricas_lstm"]:
        datos[n] = pd.read_csv(DATA/f"{n}.csv")
    return datos


def estilo(fig, x="", y="Visitantes", alto=390):
    fig.update_layout(height=alto, margin=dict(l=12,r=20,t=38,b=15), xaxis_title=x, yaxis_title=y,
                      paper_bgcolor="#F7F6F2", plot_bgcolor="white", font=dict(color="#1E1E1E", size=14),
                      legend=dict(orientation="h", y=1.14), hovermode="closest")
    fig.update_yaxes(gridcolor="#DDDDDD", tickformat=",.0f")
    return fig


def grafica(fig, key, enlazada=False):
    return st.plotly_chart(fig, use_container_width=True, key=key, on_select="rerun" if enlazada else "ignore",
                           selection_mode="points", config={"displaylogo":False, "scrollZoom":False})


def barras(serie, color):
    fig = go.Figure(go.Bar(x=serie.values, y=serie.index, orientation="h", marker_color=color,
                           hovertemplate="%{y}<br>%{x:,.0f} visitantes<extra></extra>"))
    estilo(fig, "Visitantes", "", max(360, len(serie)*32+100))
    fig.update_xaxes(tickformat=",.0f")
    return fig


def main():
    st.set_page_config(page_title="Observatorio del flujo turístico a Guatemala", page_icon="📊", layout="wide")
    st.markdown("<style>h1,h2,h3{color:#214E66;}[data-testid='stMetric']{background:white;padding:12px;border:1px solid #D9D9D9;border-radius:6px;}</style>", unsafe_allow_html=True)
    try:
        with st.spinner("Preparando información del observatorio…"):
            datos = cargar()
    except (OSError, ValueError) as error:
        st.error(f"No se pudieron cargar los datos. Ejecute python -m src.preparar_datos. Detalle: {error}")
        st.stop()
    mensual = datos["serie_mensual_total"]
    with st.sidebar:
        st.header("Consulta del observatorio")
        periodo = st.slider("Periodo de consulta", 2009, 2026, (2009, 2026), key="periodo")
        meses = st.slider("Meses incluidos de cada año", 1, 12, (1,12), key="meses")
        nivel = st.selectbox("Nivel de detalle temporal", ["Mensual", "Trimestral", "Anual"], key="nivel")
        promedio = st.checkbox("Mostrar promedio del periodo", True)
        visibles = st.multiselect("Gráficas que desea consultar", VISTAS, default=VISTAS, key="vistas")
        st.caption("Visitantes = turistas + excursionistas. La categoría general Viajero se excluye.")
        if periodo[1] == 2026:
            st.warning("2026 solo cubre enero a junio. Use meses 1–6 para comparar el mismo tramo de cada año.")
    def filtrar(df):
        return df[df.fecha.dt.year.between(*periodo) & df.fecha.dt.month.between(*meses)].copy()
    f = filtrar(mensual)
    st.title("Observatorio del flujo turístico a Guatemala")
    st.write("Explore la demanda de visitantes, identifique mercados y consulte el error de modelos ya evaluados. Las cifras son registros de ingreso; una persona puede aparecer en más de un ingreso.")
    st.caption(f"Consulta: {periodo[0]}–{periodo[1]}, meses {meses[0]}–{meses[1]}. Las vistas de modelos y estacionalidad tienen periodos fijos indicados junto a cada gráfica.")
    if f.empty:
        st.info("No hay información para esta combinación de años y meses. Amplíe el periodo o incluya enero a junio de 2026.")
        return
    fv = filtrar(datos["serie_mensual_por_via"])
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Ingresos de visitantes", f"{f.viajeros.sum()/1e6:,.2f} M", help="M equivale a un millón de ingresos registrados.")
    k2.metric("Participación terrestre", f"{fv.Terrestre.sum()/f.viajeros.sum():.1%}" if f.viajeros.sum() else "Sin flujo")
    pico = f.loc[f.viajeros.idxmax()]
    k3.metric("Mes con mayor flujo", f"{MESES[pico.fecha.month-1]} {pico.fecha.year}")
    k4.metric("Meses con información", str(len(f)))
    if not visibles:
        st.info("Seleccione al menos una gráfica en la barra lateral.")
    exploracion, mercados, modelos, metodo = st.tabs(["Exploración", "Mercados y acceso", "Estacionalidad y modelos", "Metodología"])
    with exploracion:
        fechas = f.fecha.tolist()
        firma = (periodo, meses, nivel)
        if st.session_state.get("firma_consulta") != firma:
            st.session_state["mes_detalle"] = fechas[-1]
            st.session_state["firma_consulta"] = firma
            st.session_state["evento_consumido"] = None
        if "Evolución" in visibles:
            st.subheader("1 Evolución del ingreso de visitantes")
            st.caption("¿Cuándo aumenta la demanda? Seleccione un punto para actualizar el desglose por vía. El zoom y el nivel mensual, trimestral o anual permiten cambiar el detalle.")
            temporal = agregar(f, nivel)
            fig = go.Figure(go.Scatter(x=temporal.fecha, y=temporal.viajeros, mode="lines+markers", name="Observado",
                            line=dict(color=C["azul"], width=2.5), marker=dict(size=7),
                            customdata=temporal.fecha.dt.strftime("%Y-%m-%d").to_numpy().reshape(-1,1),
                            hovertemplate="%{x|%Y-%m}<br>%{y:,.0f} visitantes<extra></extra>"))
            if promedio:
                fig.add_hline(y=temporal.viajeros.mean(), line_dash="dash", line_color=C["ocre"], annotation_text="Promedio de los puntos visibles")
            estilo(fig, "Inicio del periodo", alto=430)
            fig.update_layout(clickmode="event+select")
            fig.add_vrect(x0="2020-03-01", x1="2021-12-31", fillcolor=C["coral"], opacity=.12, line_width=0)
            fig.update_xaxes(rangeslider=dict(visible=True))
            evento = grafica(fig, "serie_"+str(firma), True)
            if evento.get("selection", {}).get("points"):
                fecha = fecha_del_evento(evento, temporal.fecha, temporal.fecha.iloc[-1])
                sello = (firma, fecha.isoformat())
                if st.session_state.get("evento_consumido") != sello:
                    freq = {"Mensual":"M", "Trimestral":"Q", "Anual":"Y"}[nivel]
                    candidatos = f[f.fecha.dt.to_period(freq).eq(fecha.to_period(freq))]
                    if not candidatos.empty:
                        st.session_state["mes_detalle"] = candidatos.fecha.max()
                    st.session_state["evento_consumido"] = sello
            if nivel != "Mensual":
                st.caption("Los puntos agregados suman solo los meses incluidos. Al seleccionar un trimestre o año se abre su último mes disponible; ajuste el mes debajo para explorar el intervalo.")
        seleccionado = st.selectbox("Mes para el desglose por vía", fechas, format_func=lambda x:f"{MESES[x.month-1]} {x.year}", key="mes_detalle")
        if "Vías" in visibles:
            st.subheader("2 Vía de ingreso del mes seleccionado")
            detalle = fv[fv.fecha.eq(seleccionado)]
            if detalle.empty:
                st.info("No hay desglose para el mes seleccionado.")
            else:
                valores = detalle.iloc[0][VIAS].astype(float)
                fig = go.Figure(go.Bar(x=VIAS, y=valores, marker_color=[COLORES_VIA[v] for v in VIAS],
                                 hovertemplate="%{x}<br>%{y:,.0f} visitantes<extra></extra>"))
                grafica(estilo(fig, "Vía"), "vias")
                st.caption(f"Mes seleccionado: {MESES[seleccionado.month-1]} {seleccionado.year}. Permite orientar la capacidad de acceso. El detalle marítimo es limitado desde 2017; un cero registrado no demuestra ausencia de actividad.")
    with mercados:
        st.caption("Estas tres vistas responden a los filtros de años y meses. Los rankings muestran cantidades registradas, sin inferir motivos de viaje ni causas de cambio.")
        reg = filtrar(datos["regiones"])
        opciones = sorted(reg["Región"].unique())
        region = st.selectbox("Región para explorar países", ["Todas"]+opciones, key="region")
        top = st.slider("Cantidad de países o fronteras", 3, 20, 10)
        if "Regiones" in visibles:
            st.subheader("3 Evolución por región de residencia")
            st.caption("¿Qué mercados regionales aportan al flujo? Use la leyenda para ocultar o mostrar series; el selector de región modifica el ranking de países.")
            fig = go.Figure()
            mayores = reg.groupby("Región").viajeros.sum().nlargest(4).index
            resumen = reg.copy()
            resumen["Región"] = resumen["Región"].where(resumen["Región"].isin(mayores), "Otras regiones")
            resumen = resumen.groupby(["fecha", "Región"]).viajeros.sum().reset_index()
            for i, (nombre, parte) in enumerate(resumen.groupby("Región")):
                a = agregar(parte[["fecha", "viajeros"]], nivel)
                fig.add_trace(go.Scatter(x=a.fecha, y=a.viajeros, mode="lines", name=nombre,
                              line=dict(color=[C["azul"],C["turquesa"],C["verde"],"#615B84",C["gris"]][i], dash="dash" if nombre=="Otras regiones" else "solid"), hovertemplate="%{x|%Y-%m}<br>%{y:,.0f}<extra>%{fullData.name}</extra>"))
            grafica(estilo(fig, "Inicio del periodo", alto=470), "regiones")
            st.caption("Se muestran las cuatro regiones con mayor flujo del periodo y se agrupan las restantes en Otras regiones. El selector de países conserva todas las regiones originales.")
        if "Mercados" in visibles:
            st.subheader("4 Países de residencia con mayor flujo")
            m = filtrar(datos["mercados"])
            if region != "Todas":
                m = m[m["Región"].eq(region)]
            if m.empty:
                st.info("La región seleccionada no tiene registros en este periodo.")
            else:
                grafica(barras(ranking(m, "País", top), C["turquesa"]), "mercados")
            st.caption("Apoya la priorización de mercados según volumen. Desde 2023 cambia el detalle por país: no interprete cambios de registro como cambios de demanda sin validar la fuente.")
        if "Fronteras" in visibles:
            st.subheader("5 Puntos de ingreso con mayor flujo")
            via = st.selectbox("Vía para consultar fronteras", ["Todas"]+VIAS)
            b = filtrar(datos["fronteras"])
            if via != "Todas":
                b = b[b["Vía"].eq(via)]
            if b.empty or b.viajeros.sum()==0:
                st.info("No hay flujo registrado para esta vía y periodo. Revise las limitaciones de cobertura.")
            else:
                grafica(barras(ranking(b, "Frontera", top), C["verde"]), "fronteras")
            st.caption("Permite localizar concentraciones de ingreso para revisar capacidad operativa; las categorías de frontera pueden cambiar con la fuente.")
    with modelos:
        st.info("Estas vistas reutilizan resultados guardados. Los filtros históricos de la barra lateral no recalculan modelos ni modifican la referencia estacional.")
        if "Estacionalidad" in visibles:
            st.subheader("6 Patrón estacional de referencia 2009 a 2019")
            e = datos["indice_estacional"]
            fig = go.Figure(go.Bar(x=MESES, y=e.indice_estacional, marker_color=C["turquesa"], hovertemplate="%{x}<br>Índice %{y:.1f}<extra></extra>"))
            fig.add_hline(y=100, line_dash="dash", line_color=C["gris"], annotation_text="Promedio anual = 100")
            grafica(estilo(fig, "Mes", "Índice estacional"), "estacional")
            st.caption("¿En qué meses planificar capacidad? Cada mes se divide por el promedio de su año y luego se promedia entre años completos. Un índice 120 indica 20 % sobre la referencia. El patrón histórico no garantiza la demanda futura.")
        if "Modelos" in visibles:
            st.subheader("7 Error de modelos del Laboratorio 1")
            m = datos["metricas_modelos"]
            simples = ["Suavizamiento exponencial simple", "Holt-Winters aditivo", "Seasonal naive"]
            elegidos = st.multiselect("Modelos a comparar", m.modelo.tolist(), default=simples, key="modelos")
            metrica = st.radio("Medida del error", ["RMSE", "MAE"], horizontal=True)
            st.caption("MAE es el error absoluto medio. RMSE da más peso a errores grandes. Ambos están en visitantes y un valor menor indica menor error en la prueba histórica.")
            mm = m[m.modelo.isin(elegidos)].sort_values(metrica.lower(), ascending=False)
            if mm.empty:
                st.info("Seleccione modelos para consultar su desempeño.")
            else:
                s = mm.set_index("modelo")[metrica.lower()]
                fig = barras(s, C["gris"])
                fig.update_layout(xaxis_title=f"{metrica} en visitantes · menor es mejor")
                grafica(fig, "modelos_error")
                st.caption(f"Menor {metrica} entre los seleccionados: {s.idxmin()} ({s.min():,.0f}). La comparación no asegura igual desempeño futuro.")
                st.dataframe(mm, hide_index=True, width="stretch")
            st.caption("Fuente: exportación original del Lab 1, serie Total mensual, división cronológica 70/30: 147 meses de entrenamiento y 63 de prueba (abril 2021–junio 2026). Prophet figura como respaldo aditivo porque la librería no estaba disponible. No equivale a un ajuste del paquete Prophet.")
        if "Predicción LSTM" in visibles:
            st.subheader("8 Predicción histórica y observaciones LSTM")
            p = datos["predicciones_lstm"]
            opciones = dict(p[["serie", "clave"]].drop_duplicates().itertuples(index=False, name=None))
            serie = st.selectbox("Serie modelada", list(opciones))
            parte = p[p.clave.eq(opciones[serie])].sort_values("fecha")
            fig = go.Figure()
            for col, nombre, color, dash in [("real", "Observado", C["azul"], "solid"), ("prediccion", "Estimado LSTM", C["coral"], "dash")]:
                fig.add_trace(go.Scatter(x=parte.fecha, y=parte[col], name=nombre, mode="lines", line=dict(color=color,dash=dash), hovertemplate="%{x|%Y-%m}<br>%{y:,.0f}<extra>%{fullData.name}</extra>"))
            estilo(fig, "Mes", alto=430).update_layout(hovermode="x unified")
            grafica(fig, "lstm")
            met = datos["metricas_lstm"][datos["metricas_lstm"].clave.eq(opciones[serie])]
            if not met.empty:
                r = met.iloc[0]
                st.caption(f"Resultado guardado del Lab 2: MAE {r.mae_test:,.0f}; RMSE {r.rmse_test:,.0f}; sMAPE {r.smape_test:.1f} %. sMAPE expresa un error porcentual simétrico.")
            st.caption(f"Evaluación histórica: {parte.fecha.min():%Y-%m} a {parte.fecha.max():%Y-%m}. No es un pronóstico de meses futuros y no incluye intervalos de incertidumbre. Las métricas del Lab 2 se presentan por separado de las del Lab 1.")
    with metodo:
        st.subheader("Fuente y alcance")
        st.write("Base académica Base_Migracion_2009-2026jun.xlsx, hoja Datos. Se agregan Turista y Excursionista entre enero de 2009 y junio de 2026. No se deduplican personas: las cifras representan ingresos registrados. País y región corresponden a la clasificación disponible en la fuente.")
        st.subheader("Límites para decidir")
        st.markdown("- Base de uso académico; no es una publicación oficial.\n- Desde 2023 cambian metodología y detalle por país.\n- La vía marítima pierde detalle desde 2017.\n- 2020 y 2021 son atípicos; la gráfica no identifica causas.\n- 2026 es parcial. Compare enero a junio entre años si necesita la misma cobertura.\n- Los decimales se deben a estimaciones expandidas de encuesta.\n- El error histórico no garantiza exactitud futura; no se estiman nuevas predicciones en este laboratorio.")
        st.subheader("Cómo usar los resultados")
        st.write("Use la evolución y las vías para revisar capacidad de acceso. Consulte países y fronteras para localizar concentraciones. El patrón estacional orienta escenarios de carga, pero requiere validación con condiciones actuales. Los modelos permiten revisar error de estimación sin atribuir causas ni recomendar inversiones por sí solos.")
        st.caption("Paleta: azul para observaciones; turquesa y verde para comparaciones; ocre para referencia; coral para estimaciones y periodos atípicos. Leyendas, etiquetas y líneas discontinuas complementan el color.")
        with st.expander("Descargar datos de la consulta"):
            st.download_button("Serie mensual filtrada CSV", f.to_csv(index=False).encode("utf-8-sig"), "consulta_visitantes.csv", "text/csv")
        informe = ROOT/"docs/informe_final.pdf"
        if informe.exists():
            st.download_button("Documento de diseño PDF", informe.read_bytes(), "informe_final.pdf", "application/pdf")
