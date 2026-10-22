# Avance del Laboratorio 10

El prototipo utiliza los datos del proyecto sobre ingreso de turistas y excursionistas a Guatemala. Incluye una serie mensual enlazada con el desglose por vía de ingreso, el patrón estacional, la comparación de cinco modelos del Laboratorio 1 y las predicciones LSTM del Laboratorio 2.

## Ejecución

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Interacción principal

1. Seleccione el periodo desde la barra lateral.
2. Haga clic en un punto de la serie histórica.
3. La gráfica de vías de ingreso cambia al mes seleccionado.
4. Use las pestañas para consultar estacionalidad, modelos y limitaciones.

## Datos

Los archivos de `datos/` se derivan de la base académica `Base_Migracion_2009-2026jun.xlsx` usada en los laboratorios 1, 2 y 9. El tablero filtra las categorías `Turista` y `Excursionista`; no suma la categoría general `Viajero`.

La base cubre enero de 2009 a junio de 2026. Deben considerarse el cambio metodológico desde 2023, la pérdida de detalle marítimo desde 2017, el periodo atípico 2020–2021 y la cobertura parcial de 2026.

## Estructura

- `app.py`: aplicación Streamlit.
- `datos/`: series procesadas, métricas y predicciones.
- `figuras/`: imágenes utilizadas en el informe.
- `generar_figuras.py`: script para reproducir las figuras del informe.
- `informe_avance.pdf`: informe de avance compilado.
