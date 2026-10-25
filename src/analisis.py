"""Transformaciones compartidas por el tablero y sus verificaciones."""
import pandas as pd


def agregar(serie, nivel):
    frecuencia = {"Mensual": "MS", "Trimestral": "QS", "Anual": "YS"}[nivel]
    grupos = serie.set_index("fecha").resample(frecuencia)
    totales = grupos.sum(numeric_only=True)
    # Los meses excluidos por el usuario no son observaciones de flujo cero.
    return totales.loc[grupos.size().gt(0)].reset_index()


def fecha_del_evento(evento, fechas, respaldo):
    """Ignora selecciones antiguas que quedaron fuera del filtro visible."""
    puntos = evento.get("selection", {}).get("points", []) if evento else []
    if puntos:
        dato = puntos[-1].get("customdata")
        if dato:
            fecha = pd.Timestamp(dato[0])
            if fecha in set(pd.to_datetime(fechas)):
                return fecha
    return pd.Timestamp(respaldo)


def ranking(datos, columna, n=10):
    return datos.groupby(columna).viajeros.sum().nlargest(n).sort_values()
