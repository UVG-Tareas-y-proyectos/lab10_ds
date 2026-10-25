# Diccionario de datos

La unidad del tablero es el ingreso registrado de un turista o excursionista, no una persona única. Fuente: `data/raw/Base_Migracion_2009-2026jun.xlsx`, hoja `Datos`. Base académica, no publicación oficial.

| Campo de origen | Uso |
| --- | --- |
| Año, Mes cod | Construyen `fecha`, primer día del mes |
| Tipo de Viajero | Solo Turista y Excursionista; excluye Viajero y Cruceristas como categorías independientes |
| Viajero | Cantidad expandida de ingresos, admite decimales |
| Vía | Aérea, Marítima o Terrestre |
| País, Región | Clasificación de residencia disponible en cada fuente |
| Frontera | Punto de ingreso según la fuente |

Los grupos sin etiqueta se conservan como `Sin especificar`. No se deduplican personas ni se interpretan ceros como ausencia de actividad. Cobertura: 210 meses, enero 2009–junio 2026; 137,642 registros filtrados y 46,711,912.8865 ingresos.

## Archivos reproducidos en data/processed

- `serie_mensual_total.csv`: fecha, viajeros.
- `serie_mensual_por_via.csv`: fecha y cantidades por vía.
- `mercados.csv`: fecha, Región, País, viajeros.
- `regiones.csv`: fecha, Región, viajeros.
- `fronteras.csv`: fecha, Vía, Frontera, viajeros.
- `indice_estacional.csv`: mes numérico e índice base 100; promedio de razones mes/promedio de su año para años completos 2009–2019.
- `metricas_modelos.csv`: modelo, mae, rmse; conserva resultados exportados de `data/raw/modelos_lab1.csv` para Total mensual. División cronológica 70/30, 147 meses de entrenamiento y 63 de prueba. No se reentrena.
- `predicciones_lstm.csv`: clave, serie, fecha, real, prediccion. Se conserva el resultado del Lab 2 incluido en el avance.
- `metricas_lstm.csv`: configuración, arquitectura, ventana y errores del Lab 2. No se mezclan con el ranking del Lab 1.
- `auditoria.json`: conteos, total y SHA256 de cada fuente.

## Procedencia y correcciones respecto del avance

`data/raw/modelos_lab1.csv` es la exportación original de `data/processed/comparacion_modelos.csv` del Laboratorio 1 entregado por el equipo. Sus métricas difieren de las transcritas en `datos/metricas_modelos_serie_total.csv` del avance. El tablero final usa la exportación verificable. Por ejemplo, SES registra RMSE 180,598.23; Holt-Winters aditivo 184,529.72; Seasonal naive 219,663.87. Prophet aparece como `Prophet - respaldo aditivo`: no representa un entrenamiento de la biblioteca Prophet. El archivo del avance se conserva para trazabilidad.

`datos/` y los informes de avance conservan el material recibido. Las nuevas tablas se generan desde `data/raw/` y no se versionan, siguiendo la estructura del curso. El total mensual se contrasta con el avance antes de generar resultados.

## Límites

Cambian fuentes y metodología desde 2023; disminuye el detalle marítimo desde 2017. Los años 2020–2021 son atípicos y 2026 solo contiene enero–junio. Los modelos se evalúan sobre observaciones históricas y no aportan pronósticos futuros ni intervalos nuevos. Seleccionar enero–junio permite comparar coberturas equivalentes entre años; no elimina cambios metodológicos.
