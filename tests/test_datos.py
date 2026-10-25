from pathlib import Path
import json
import numpy as np
import pandas as pd
from src.analisis import agregar, fecha_del_evento

ROOT = Path(__file__).resolve().parents[1]
D = ROOT/"data/processed"


def test_conservacion_del_total_y_cobertura():
    m = pd.read_csv(D/"serie_mensual_total.csv", parse_dates=["fecha"])
    assert len(m) == 210 and not m.fecha.duplicated().any()
    assert list(m.fecha) == list(pd.date_range("2009-01-01", "2026-06-01", freq="MS"))
    assert np.isclose(m.viajeros.sum(), 46711912.88651751)
    for nombre in ["mercados", "regiones", "fronteras"]:
        g = pd.read_csv(D/f"{nombre}.csv").groupby("fecha").viajeros.sum()
        np.testing.assert_allclose(g, m.viajeros)
    vias = pd.read_csv(D/"serie_mensual_por_via.csv").drop(columns="fecha")
    np.testing.assert_allclose(vias.sum(axis=1), m.viajeros)


def test_agregaciones_y_anio_parcial():
    m = pd.read_csv(D/"serie_mensual_total.csv", parse_dates=["fecha"])
    parcial = m[m.fecha.dt.year.eq(2026)]
    assert len(parcial) == 6
    for nivel, longitud in [("Mensual",210),("Trimestral",70),("Anual",18)]:
        a = agregar(m,nivel)
        assert len(a)==longitud
        assert np.isclose(a.viajeros.sum(),m.viajeros.sum())


def test_estacionalidad_solo_referencia_completa():
    e = pd.read_csv(D/"indice_estacional.csv")
    assert list(e.mes)==list(range(1,13))
    assert np.isclose(e.indice_estacional.mean(),100)


def test_seleccion_fuera_de_filtro_y_enlace_valido():
    fechas = pd.date_range("2025-01-01", "2025-12-01", freq="MS")
    evento = {"selection":{"points":[{"customdata":["2019-12-01"]}]}}
    assert fecha_del_evento(evento,fechas,fechas[-1]) == fechas[-1]
    evento["selection"]["points"][0]["customdata"] = ["2025-03-01"]
    assert fecha_del_evento(evento,fechas,fechas[-1]) == fechas[2]


def test_modelos_conservan_fuente_y_lstm_observado():
    original = pd.read_csv(ROOT/"data/raw/modelos_lab1.csv")
    original = original[original.Serie.eq("Total mensual")]
    m = pd.read_csv(D/"metricas_modelos.csv")
    np.testing.assert_allclose(m.rmse,original.RMSE)
    np.testing.assert_allclose(m.mae,original.MAE)
    assert len(m)>=3
    p = pd.read_csv(D/"predicciones_lstm.csv")
    mensual = pd.read_csv(D/"serie_mensual_total.csv")
    unido = p[p.clave.eq("total_viajeros")].merge(mensual,on="fecha",validate="one_to_one")
    np.testing.assert_allclose(unido.real,unido.viajeros)
    auditoria = json.loads((D/"auditoria.json").read_text(encoding="utf-8"))
    assert auditoria["registros_filtrados"]==137642
