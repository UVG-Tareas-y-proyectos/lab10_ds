"""Agrega fuentes existentes; no ajusta ni entrena modelos predictivos."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
VIAS = ["Aérea", "Marítima", "Terrestre"]


def preparar(root=ROOT):
    raw, out = root / "data/raw", root / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    fuente = raw / "Base_Migracion_2009-2026jun.xlsx"
    d = pd.read_excel(fuente, sheet_name="Datos", usecols=["Año", "Mes cod", "Vía", "Frontera", "País", "Región", "Tipo de Viajero", "Viajero"])
    for c in ["Vía", "Frontera", "País", "Región", "Tipo de Viajero"]:
        d[c] = d[c].astype("string").str.strip()
    d = d[d["Tipo de Viajero"].isin(["Turista", "Excursionista"])].copy()
    d["Viajero"] = pd.to_numeric(d["Viajero"], errors="raise")
    if not np.isfinite(d.Viajero).all() or d.Viajero.lt(0).any():
        raise ValueError("La fuente contiene cantidades inválidas.")
    d["fecha"] = pd.to_datetime(dict(year=d["Año"], month=d["Mes cod"], day=1))
    for c in ["Vía", "Frontera", "País", "Región"]:
        d[c] = d[c].fillna("Sin especificar")
    mensual = d.groupby("fecha").Viajero.sum().rename("viajeros").reset_index()
    esperado = pd.date_range("2009-01-01", "2026-06-01", freq="MS")
    if not mensual.fecha.equals(pd.Series(esperado, name="fecha")):
        raise ValueError("La cobertura debe ser de 210 meses consecutivos.")
    anterior = pd.read_csv(root/"datos/serie_mensual_total.csv")
    if not np.allclose(mensual.viajeros, anterior.viajeros, atol=1e-5, rtol=1e-10):
        raise ValueError("La base no reproduce la serie del avance.")
    mensual.to_csv(out/"serie_mensual_total.csv", index=False)
    vias = d.pivot_table(index="fecha", columns="Vía", values="Viajero", aggfunc="sum", fill_value=0).reindex(columns=VIAS, fill_value=0)
    if not np.allclose(vias.sum(axis=1), mensual.viajeros):
        raise ValueError("Las vías no suman el total de visitantes.")
    vias.to_csv(out/"serie_mensual_por_via.csv")
    for nombre, columnas in [("mercados", ["Región", "País"]), ("regiones", ["Región"]), ("fronteras", ["Vía", "Frontera"])]:
        d.groupby(["fecha"]+columnas, dropna=False).Viajero.sum().rename("viajeros").reset_index().to_csv(out/f"{nombre}.csv", index=False)
    # Cada mes se divide por el promedio de su propio año completo de 2009-2019.
    ref = mensual[mensual.fecha.dt.year.between(2009, 2019)].copy()
    ref["indice_estacional"] = 100*ref.viajeros/ref.groupby(ref.fecha.dt.year).viajeros.transform("mean")
    ref.groupby(ref.fecha.dt.month).indice_estacional.mean().rename_axis("mes").to_csv(out/"indice_estacional.csv")
    modelos = pd.read_csv(raw/"modelos_lab1.csv")
    modelos = modelos[modelos.Serie.eq("Total mensual")].rename(columns={"Modelo":"modelo", "MAE":"mae", "RMSE":"rmse"})
    modelos[["modelo", "mae", "rmse"]].to_csv(out/"metricas_modelos.csv", index=False)
    for nombre in ["predicciones_lstm.csv", "metricas_lstm.csv"]:
        (out/nombre).write_bytes((raw/nombre).read_bytes())
    auditoria = {"registros_filtrados": len(d), "meses": len(mensual), "total": float(mensual.viajeros.sum()), "fuentes_sha256": {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(raw.iterdir()) if p.suffix in [".xlsx", ".csv"]}, "modelos": "Métricas exportadas del Lab 1; no se entrenan modelos en Lab 10"}
    (out/"auditoria.json").write_text(json.dumps(auditoria, ensure_ascii=False, indent=2), encoding="utf-8")
    return auditoria


if __name__ == "__main__":
    print(json.dumps(preparar(), ensure_ascii=False, indent=2))
