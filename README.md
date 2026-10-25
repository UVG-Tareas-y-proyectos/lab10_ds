# Laboratorio 10 Visualización interactiva

Observatorio del flujo turístico a Guatemala para directivos y responsables de planificación. Integra ocho visualizaciones interactivas con datos académicos de turistas y excursionistas, resultados guardados del Laboratorio 1 y predicciones históricas LSTM del Laboratorio 2. No entrena modelos nuevos.

## Ejecutar

Requiere Python 3.11 o 3.12. Desde la raíz:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.preparar_datos
python -m streamlit run app.py
```

En macOS/Linux active el entorno con `source .venv/bin/activate`. También se puede ejecutar directamente con `.venv\Scripts\python.exe -m streamlit run app.py` en Windows, sin cambiar la política de PowerShell. Si faltan los procesados, la primera apertura los genera; esta preparación puede tardar al leer el Excel. Después se carga la información en caché. No se necesita una clave ni un servicio externo.

## Recorrido de uso

1. Seleccione años y meses en la barra lateral. Para comparar 2026 con años anteriores use los meses 1–6.
2. Elija nivel mensual, trimestral o anual y las gráficas que quiere consultar.
3. En **Exploración**, haga clic en un punto de la serie: cambiarán el selector de mes y las barras por vía. Los puntos agregados abren el último mes disponible de su intervalo; el selector permite consultar los demás meses.
4. En **Mercados y acceso**, consulte regiones, elija una región para el ranking de países y filtre las fronteras por vía.
5. En **Estacionalidad y modelos**, compare tres modelos simples preseleccionados (SES, Holt-Winters y Seasonal naive), alterne MAE/RMSE o elija modelos adicionales. Consulte observado y estimado LSTM por serie. Estas vistas conservan su periodo de referencia y no cambian con los filtros históricos.
6. En **Metodología**, revise las restricciones y descargue la consulta o el documento de diseño.

Todas las gráficas permiten consultar valores emergentes y usar zoom; las de líneas permiten ocultar series con la leyenda. Las tarjetas, controles y tablas no se cuentan como gráficas.

## Ocho visualizaciones

| Vista | Pregunta de gestión | Interacción |
| --- | --- | --- |
| 1 Evolución temporal | ¿Cuándo aumenta o disminuye el flujo? | Filtros, zoom, escala temporal y selección de puntos |
| 2 Desglose por vía | ¿Cómo se reparte el mes consultado? | Enlace desde la serie, selector alternativo y zoom |
| 3 Evolución regional | ¿Qué mercados regionales aportan al flujo? | Periodo, nivel de detalle y leyenda |
| 4 Países de residencia | ¿Qué países concentran ingresos en una región? | Región, periodo y cantidad de países |
| 5 Puntos de ingreso | ¿Dónde se concentra el acceso? | Vía, periodo y cantidad de fronteras |
| 6 Índice estacional | ¿Qué meses superan la referencia histórica? | Hover y zoom; referencia fija 2009–2019 |
| 7 Error de modelos | ¿Qué error registran los modelos ya evaluados? | Selección de modelos, MAE/RMSE, hover y zoom |
| 8 Observado y LSTM | ¿Dónde difiere la estimación del registro? | Serie modelada, leyenda y zoom |

## Estructura

Se adopta la convención de [CC3084 del catedrático](https://github.com/menene/cc3084-2026-02-40):

```text
app.py                       entrada compatible con el avance
src/
  preparar_datos.py           agregaciones, validaciones y auditoría
  analisis.py                 transformaciones de consulta
  tablero.py                  interfaz Streamlit y ocho gráficas
  generar_figuras.py          ilustraciones reproducibles del informe
  generar_informe.py          edición del formato del avance en una copia
  exportar_pdf.ps1            exportación opcional con Word en Windows
notebooks/
  visualizacion-interactiva.ipynb
data/raw/                    fuente y resultados anteriores sin modificar
data/processed/              derivados reproducibles, no versionados
docs/                        únicamente el informe final PDF
figuras/                     ilustraciones del informe
tests/                       verificaciones de datos e interfaz
codebook.md                  variables, procedencia y limitaciones
requirements.txt             dependencias de ejecución verificadas
```

`datos/` conserva los datos del avance como referencia. Los documentos de la entrega parcial están disponibles en el historial de Git; la entrega actual incluye únicamente el informe final PDF. La aplicación final lee los derivados de `data/processed/`.

## Fuentes y corrección de métricas

La base cubre enero de 2009 a junio de 2026. Se filtran Turista y Excursionista, sin sumar Viajero ni la categoría independiente Cruceristas. Las cifras representan ingresos registrados, no personas únicas. Las sumas se contrastan con la serie del avance antes de generar las tablas nuevas.

El ranking final usa la exportación original del Lab 1 en `data/raw/modelos_lab1.csv`. Difiere de la transcripción del avance: entre los tres modelos simples, SES presenta RMSE 180,598.23, Holt-Winters 184,529.72 y Seasonal naive 219,663.87. Los resultados originales se conservan sin volver a entrenar. `Prophet - respaldo aditivo` identifica una alternativa empleada en el Lab 1 cuando Prophet no estaba disponible; no equivale a la biblioteca Prophet. Las métricas LSTM se presentan por separado. El [diccionario de datos](codebook.md) documenta los campos y la procedencia.

Hay cambio metodológico desde 2023, pérdida de detalle marítimo desde 2017, un periodo atípico 2020–2021 y cobertura parcial de 2026. Los ceros registrados no demuestran ausencia de actividad. Las predicciones mostradas corresponden a evaluación histórica y no garantizan resultados futuros.

## Verificación

```powershell
python -m pip install -r requirements-dev.txt
python -m src.preparar_datos
python -m pytest -q
```

Se incluyen once pruebas de conservación de totales, cobertura, agregaciones, selección fuera de filtro, procedencia de métricas, ocho gráficas, filtros, tres niveles temporales, estados sin datos y selección de modelos. El enlace se comprueba además en navegador: seleccionar diciembre de 2014 actualiza el mes y las barras por vía.

## Documento de diseño

- [Informe final PDF](docs/informe_final.pdf)

Para regenerar las ilustraciones y preparar el documento temporal desde una clonación con historial completo:

```powershell
python -m pip install -r requirements-dev.txt
python generar_figuras.py
python -m src.generar_informe
```

El generador recupera la plantilla del historial de Git y escribe el Word temporal en `work/`, que no se versiona. Si se usa un ZIP sin historial, se puede proporcionar una plantilla externa con `python -m src.generar_informe --plantilla RUTA`.

En Windows con Microsoft Word instalado puede actualizarse el PDF con:

```powershell
.\src\exportar_pdf.ps1 -InputPath .\work\informe_final.docx -OutputPath .\docs\informe_final.pdf
```

Revise visualmente el PDF después de regenerarlo. `docs/` contiene solo la entrega final en PDF.
