import json
import pandas as pd
from streamlit.testing.v1 import AppTest


def iniciar():
    at = AppTest.from_file("app.py", default_timeout=30).run()
    assert not at.exception
    return at


def test_ocho_vistas_y_tres_modelos_simples():
    at = iniciar()
    assert len(at.get("plotly_chart")) == 8
    assert len(at.multiselect(key="modelos").value) == 3
    assert at.metric[3].value == "210"


def test_filtros_y_tres_niveles_temporales():
    at = iniciar()
    for nivel in ["Trimestral", "Anual", "Mensual"]:
        at.sidebar.selectbox(key="nivel").select(nivel).run()
        assert not at.exception and len(at.get("plotly_chart")) == 8
    at.sidebar.slider(key="periodo").set_value((2025,2026)).run()
    at.sidebar.slider(key="meses").set_value((1,6)).run()
    assert not at.exception and at.metric[3].value == "12"
    assert at.selectbox(key="mes_detalle").value == pd.Timestamp("2026-06-01")


def test_periodo_sin_informacion():
    at = iniciar()
    at.sidebar.slider(key="periodo").set_value((2026,2026)).run()
    at.sidebar.slider(key="meses").set_value((7,12)).run()
    assert not at.exception and len(at.get("plotly_chart")) == 0
    assert any("No hay información" in x.value for x in at.info)


def test_ocultar_vistas_y_modelos_sin_seleccion():
    at = iniciar()
    at.sidebar.multiselect(key="vistas").set_value(["Modelos"]).run()
    assert len(at.get("plotly_chart")) == 1
    at.multiselect(key="modelos").set_value([]).run()
    assert not at.exception
    assert any("Seleccione modelos" in x.value for x in at.info)
    at.sidebar.multiselect(key="vistas").set_value([]).run()
    assert not at.exception and len(at.get("plotly_chart")) == 0


def test_seleccion_alternativa_del_mes_y_cambio_de_filtro():
    at = iniciar()
    at.selectbox(key="mes_detalle").select(pd.Timestamp("2019-12-01")).run()
    assert not at.exception
    assert any("Mes seleccionado: Dic 2019" in x.value for x in at.caption)
    at.sidebar.slider(key="periodo").set_value((2025,2025)).run()
    assert not at.exception
    assert at.selectbox(key="mes_detalle").value.year == 2025


def test_mercado_via_y_serie_lstm():
    at = iniciar()
    at.selectbox(key="region").select("AMÉRICA DEL NORTE").run()
    assert not at.exception
    via = next(x for x in at.selectbox if x.label == "Vía para consultar fronteras")
    via.select("Marítima").run()
    lstm = next(x for x in at.selectbox if x.label == "Serie modelada")
    lstm.select(lstm.options[-1]).run()
    assert not at.exception
