# Datos utilizados

## Fuente principal

`Base_Migracion_2009-2026jun.xlsx`, hoja `Datos`, utilizada en los laboratorios 1, 2 y 9. La copia de referencia se encuentra en:

`../Lab 9/Laboratorio-9-Infografia/data/raw/Base_Migracion_2009-2026jun.xlsx`

La fuente indica que la base es de uso académico y no corresponde a una publicación oficial.

## Archivos del tablero

- `serie_mensual_total.csv`: suma mensual de turistas y excursionistas.
- `serie_mensual_por_via.csv`: suma mensual por vía aérea, marítima y terrestre.
- `indice_estacional.csv`: índice mensual calculado con 2009–2019 y base 100.
- `metricas_modelos_serie_total.csv`: MAE y RMSE de cinco modelos del Laboratorio 1.
- `predicciones_lstm.csv`: valores observados y predicciones del Laboratorio 2.
- `metricas_lstm.csv`: métricas de prueba de los modelos LSTM seleccionados.
- `kpis_avance.csv`: indicadores calculados en el Laboratorio 9.
- `comparacion_series.csv`: resultados comparativos del Laboratorio 9.

## Restricciones

- Se emplean únicamente `Turista` y `Excursionista` para representar visitantes.
- Desde 2023 existe un cambio metodológico y menor detalle por país.
- La vía marítima pierde detalle desde 2017.
- 2026 contiene enero–junio.
- Los valores decimales son estimaciones expandidas de encuesta.
