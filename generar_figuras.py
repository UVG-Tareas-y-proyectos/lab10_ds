from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import Rectangle


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "datos"
SALIDA = BASE_DIR / "figuras"
SALIDA.mkdir(exist_ok=True)

COLORES = {
    "azul": "#214E66",
    "turquesa": "#2A7F8E",
    "ocre": "#D7A84B",
    "coral": "#C96B4B",
    "verde": "#6C7A59",
    "gris": "#7C8991",
}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})

mensual = pd.read_csv(DATA_DIR / "serie_mensual_total.csv", parse_dates=["fecha"])
vias = pd.read_csv(DATA_DIR / "serie_mensual_por_via.csv", parse_dates=["fecha"])
estacional = pd.read_csv(DATA_DIR / "indice_estacional.csv")
modelos = pd.read_csv(DATA_DIR / "metricas_modelos_serie_total.csv")
pred_lstm = pd.read_csv(DATA_DIR / "predicciones_lstm.csv", parse_dates=["fecha"])

# Serie mensual del flujo turístico.
fig, ax = plt.subplots(figsize=(11, 4.8))
ax.plot(mensual.fecha, mensual.viajeros / 1_000, color=COLORES["azul"], linewidth=2)
ax.axvspan(
    pd.Timestamp("2020-03-01"),
    pd.Timestamp("2021-12-31"),
    color=COLORES["coral"],
    alpha=0.12,
    label="Periodo atípico 2020–2021",
)
ax.set_xlabel("Año")
ax.set_ylabel("Visitantes mensuales (miles)")
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, loc="upper left")
fig.tight_layout()
fig.savefig(SALIDA / "evolucion_mensual.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Desglose por vía para diciembre de 2019, mes máximo de la serie.
fecha_referencia = mensual.loc[mensual.viajeros.idxmax(), "fecha"]
detalle = vias[vias.fecha == fecha_referencia].iloc[0]
nombres_via = ["Aérea", "Marítima", "Terrestre"]
valores_via = detalle[nombres_via].astype(float) / 1_000
fig, ax = plt.subplots(figsize=(8.8, 4.4))
barras = ax.bar(
    nombres_via,
    valores_via,
    color=[COLORES["azul"], COLORES["turquesa"], COLORES["ocre"]],
)
ax.set_ylabel("Visitantes (miles)")
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
for barra, valor in zip(barras, valores_via):
    ax.text(barra.get_x() + barra.get_width() / 2, valor + 5, f"{valor:,.0f}", ha="center")
fig.tight_layout()
fig.savefig(SALIDA / "vias_diciembre_2019.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Índice estacional pre-pandemia.
fig, ax = plt.subplots(figsize=(9.5, 4.4))
colores_est = [COLORES["ocre"] if x >= 120 else COLORES["turquesa"] for x in estacional.indice_estacional]
ax.bar(estacional.mes, estacional.indice_estacional, color=colores_est)
ax.axhline(100, color=COLORES["gris"], linestyle="--", linewidth=1.5)
ax.set_ylabel("Índice estacional (promedio = 100)")
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(SALIDA / "indice_estacional.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Comparación de modelos del Laboratorio 1.
orden = modelos.sort_values("rmse", ascending=False)
mejor = modelos.loc[modelos.rmse.idxmin(), "modelo"]
colores_mod = [COLORES["ocre"] if x == mejor else COLORES["gris"] for x in orden.modelo]
fig, ax = plt.subplots(figsize=(9.3, 4.4))
ax.barh(orden.modelo, orden.rmse / 1_000, color=colores_mod)
ax.set_xlabel("RMSE en prueba (miles de visitantes; menor es mejor)")
ax.grid(axis="x", color="#D9D9D9", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right", "left"]].set_visible(False)
for y, valor in enumerate(orden.rmse / 1_000):
    ax.text(valor + 4, y, f"{valor:,.0f}", va="center")
fig.tight_layout()
fig.savefig(SALIDA / "comparacion_modelos.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Resultado LSTM para la serie mensual total del Laboratorio 2.
serie_lstm = pred_lstm[pred_lstm.clave == "total_viajeros"].sort_values("fecha")
fig, ax = plt.subplots(figsize=(10.5, 4.5))
ax.plot(
    serie_lstm.fecha,
    serie_lstm.real / 1_000,
    color=COLORES["azul"],
    linewidth=2.2,
    label="Valor observado",
)
ax.plot(
    serie_lstm.fecha,
    serie_lstm.prediccion / 1_000,
    color=COLORES["coral"],
    linewidth=2,
    linestyle="--",
    label="Predicción LSTM",
)
ax.set_xlabel("Fecha")
ax.set_ylabel("Visitantes mensuales (miles)")
ax.grid(axis="y", color="#D9D9D9", linewidth=0.8)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, ncol=2, loc="upper left")
fig.tight_layout()
fig.savefig(SALIDA / "prediccion_lstm.png", dpi=220, bbox_inches="tight")
plt.close(fig)

# Paleta del tablero.
paleta = [
    ("Azul profundo", "#214E66", "Serie principal"),
    ("Turquesa", "#2A7F8E", "Comparaciones"),
    ("Ocre", "#D7A84B", "Selección y énfasis"),
    ("Coral", "#C96B4B", "Advertencias"),
    ("Verde gris", "#6C7A59", "Serie secundaria"),
]
fig, ax = plt.subplots(figsize=(10.2, 2.5))
ax.set_xlim(0, len(paleta))
ax.set_ylim(0, 1)
ax.axis("off")
for i, (nombre, codigo, uso) in enumerate(paleta):
    ax.add_patch(Rectangle((i + 0.08, 0.43), 0.84, 0.45, color=codigo))
    ax.text(i + 0.5, 0.31, nombre, ha="center", fontsize=9)
    ax.text(i + 0.5, 0.19, codigo, ha="center", fontsize=8)
    ax.text(i + 0.5, 0.06, uso, ha="center", fontsize=7.5)
fig.tight_layout(pad=0.2)
fig.savefig(SALIDA / "paleta.png", dpi=220, bbox_inches="tight")
plt.close(fig)
