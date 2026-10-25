"""Completa el informe sobre una copia del avance, conservando sus partes OOXML."""
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
import argparse
import subprocess
from lxml import etree as E
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
NS = {"w":"http://schemas.openxmlformats.org/wordprocessingml/2006/main", "a":"http://schemas.openxmlformats.org/drawingml/2006/main", "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships", "wp":"http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"}
W = "{"+NS["w"]+"}"
R = "{"+NS["r"]+"}"


def generar(plantilla=None):
    if plantilla:
        fuente = Path(plantilla)
    else:
        resultado = subprocess.run(
            ['git', 'show', '99f89f4:informe_avance.docx'],
            cwd=ROOT, capture_output=True, check=False,
        )
        if resultado.returncode:
            raise RuntimeError('Se necesita el historial completo de Git o una plantilla externa indicada con --plantilla RUTA.')
        fuente = BytesIO(resultado.stdout)
    with ZipFile(fuente) as z:
        partes={n:z.read(n) for n in z.namelist()}
    doc=E.fromstring(partes["word/document.xml"])
    body=doc.find("w:body",NS)
    p=body.findall("w:p",NS)
    def cambiar(parrafo,texto):
        pr=parrafo.find("w:pPr",NS)
        rp=parrafo.find("w:r/w:rPr",NS)
        for child in list(parrafo):
            if child is not pr:parrafo.remove(child)
        r=E.SubElement(parrafo,W+"r")
        if rp is not None:r.append(deepcopy(rp))
        # Un salto de línea conserva el mismo formato de párrafo de la plantilla.
        for i,linea in enumerate(texto.split("\n")):
            if i:E.SubElement(r,W+"br")
            t=E.SubElement(r,W+"t");t.text=linea
    for idx in [4,10]:
        for t in p[idx].iter(W+"t"):
            if t.text:t.text=t.text.replace("Informe de avance","Informe final")
    for idx in [6,12]:
        for t in p[idx].iter(W+"t"):
            if t.text:t.text=t.text.replace("22 de octubre","24 de octubre")
    textos={
      15:"El tablero permite explorar los ingresos registrados de turistas y excursionistas a Guatemala, identificar mercados y puntos de acceso y consultar el error de modelos evaluados anteriormente. La versión final contiene ocho visualizaciones interactivas. La serie temporal está enlazada con el desglose mensual por vía; la consulta incluye filtros de años, meses, nivel de detalle y selección de gráficas.",
      16:"Está dirigido a directivos y responsables de planificación turística. Las preguntas de gestión orientan la navegación; las unidades, leyendas y notas permiten leer los resultados sin formación estadística. Los valores observados se distinguen de las estimaciones y las limitaciones acompañan las vistas que afectan.",
      18:"¿Cómo cambió el flujo de turistas y excursionistas y qué meses concentraron mayores ingresos?",
      19:"¿Cómo se distribuye el mes seleccionado entre las vías aérea, marítima y terrestre?",
      20:"¿Qué países de residencia aportan mayor volumen dentro de una región seleccionada?",
      21:"¿Cómo cambia el ingreso de visitantes según la región de residencia?",
      22:"¿Qué puntos de ingreso concentran el flujo y cómo cambia el ranking por vía?",
      23:"¿Qué meses superaron la referencia estacional entre 2009 y 2019?",
      24:"¿Qué error registran tres modelos simples y cómo difieren las estimaciones LSTM de las observaciones?",
      25:"¿Qué periodos tienen cobertura comparable y qué cambios de fuente limitan las conclusiones?",
      26:"Alcance de la versión final",
      27:"Se incluyen ocho gráficas: evolución temporal, vías del mes seleccionado, evolución regional, ranking de países, ranking de fronteras, índice estacional, error de modelos y observaciones frente a estimaciones LSTM. Las tarjetas, los controles y la tabla de métricas son complementarios y no se cuentan como visualizaciones.",
      28:"Se reutilizan resultados de los laboratorios 1 y 2, sin entrenar modelos nuevos. La consulta histórica permite agregar por mes, trimestre o año y acotar los meses incluidos. Las métricas y el índice estacional conservan sus periodos fijos. El tablero no identifica causas, no estima personas únicas y no genera pronósticos futuros.",
      30:"La fuente principal es Base_Migracion_2009-2026jun.xlsx, hoja Datos, con 161,036 registros y 13 variables. Se conservan Turista y Excursionista y se excluyen Viajero y la categoría independiente Cruceristas. La cantidad Viajero representa ingresos registrados; una misma persona puede aparecer en varios ingresos.",
      31:"El filtro conserva 137,642 registros. La serie contiene 210 meses y suma 46,711,912.89 ingresos entre enero de 2009 y junio de 2026. El 59.1 % corresponde a la vía terrestre y diciembre de 2019 registra el máximo mensual. Las sumas por país, región, frontera y vía reproducen el total mensual del avance.",
      33:"El proceso conserva los originales en data/raw y genera agregados en data/processed mediante src/preparar_datos.py. Se valida continuidad de meses, cantidades no negativas y conservación del total. El archivo auditoria.json registra conteos y huellas SHA256. El índice estacional usa años completos de 2009 a 2019. Las métricas de modelos se copian de resultados guardados; no se ajustan modelos.",
      41:"Se conserva la paleta del avance. Azul profundo identifica observaciones; turquesa y verde gris apoyan comparaciones; ocre señala la referencia; coral distingue estimaciones y periodos atípicos. El gris y un violeta auxiliar separan categorías regionales. Fondo claro y texto oscuro sostienen la legibilidad. La predicción también usa línea discontinua y las leyendas explican cada serie, de modo que el color no sea la única señal.",
      44:"La interfaz usa la fuente sans serif de Streamlit para favorecer la lectura en pantalla. La jerarquía distingue título, secciones y notas; las gráficas muestran unidades y valores exactos al pasar el cursor. El selector de mes ofrece una alternativa al clic sobre un punto. Los controles visibles permiten corregir la consulta sin perder el contexto.",
      46:"La barra lateral permite seleccionar años, meses, escala temporal y gráficas visibles. Exploración contiene los indicadores, la serie y su desglose enlazado. Mercados y acceso reúne regiones, países y fronteras. Estacionalidad y modelos presenta referencias históricas y evaluación predictiva. Metodología contiene definiciones, advertencias y descargas. Cada vista incluye la pregunta de gestión y su alcance.",
      48:"Bosquejo de navegación y de las ocho visualizaciones de la versión final.",
      50:"Streamlit permite integrar controles, mensajes y navegación con Python, el lenguaje empleado en los laboratorios anteriores. Plotly aporta zoom, leyendas interactivas, valores emergentes y selección de puntos. El evento de selección actualiza el mes consultado y las barras por vía. Pandas realiza agregaciones explícitas sin volver a ajustar modelos. Son herramientas gratuitas y de código abierto adecuadas para un tablero académico reproducible.",
      51:"Desde la raíz se instalan requirements.txt, se ejecuta python -m src.preparar_datos y se abre python -m streamlit run app.py. Si faltan los procesados, la primera apertura los genera. El proyecto adopta src, notebooks, data/raw y data/processed según la referencia del curso. app.py mantiene el comando del avance; las fuentes y resultados guardados permiten ejecutarlo sin servicios externos.",
      52:"Ocho visualizaciones funcionales",
      53:"1 Evolución del ingreso de visitantes",
      54:"La línea permite seguir cambios en el tiempo, una tarea adecuada para una serie ordenada. El usuario filtra años y meses, cambia entre mes, trimestre y año, usa zoom y selecciona un punto. La selección actualiza la gráfica de vías. Un punto trimestral o anual abre su último mes disponible; el selector permite consultar otros meses. Los agregados suman solamente los meses incluidos en el filtro.",
      56:"Serie mensual observada. El sombreado identifica el periodo atípico 2020 y 2021.",
      57:"2 Vía de ingreso del mes seleccionado",
      58:"Las barras comparan tres cantidades con una base común, lo que facilita distinguir diferencias entre vías. Reciben el mes seleccionado en la serie y permiten examinar valores exactos o ampliar una zona. El selector de mes conserva una alternativa accesible. Al cambiar el periodo, una selección que queda fuera del filtro se reinicia al último mes disponible. Esta vista ayuda a revisar capacidad de acceso, con reservas sobre el registro marítimo desde 2017.",
      60:"Ejemplo del desglose enlazado para diciembre de 2019.",
      61:"6 Índice estacional de referencia",
      62:"Las barras permiten comparar los doce meses con la línea de referencia 100. Para cada año completo de 2009 a 2019 se divide cada mes por el promedio de ese año y se promedian las razones entre años. Diciembre alcanza 134.9, aproximadamente 34.9 % sobre la referencia. El usuario examina valores y amplía la gráfica. Este patrón orienta escenarios de carga, sin asegurar que se repita en años futuros.",
      64:"Índice estacional reproducido con años completos de 2009 a 2019.",
      65:"7 Error de modelos del Laboratorio 1",
      66:"Las barras horizontales comparan el error con nombres de modelos legibles. La vista inicia con tres modelos simples: suavizamiento exponencial simple, Holt-Winters aditivo y Seasonal naive. Permite elegir modelos adicionales y alternar RMSE y MAE. Sus RMSE son 180,598.23, 184,529.72 y 219,663.87 visitantes, respectivamente. Entre estos tres, SES registra el menor RMSE. Los resultados corresponden a la división cronológica 70/30 del Lab 1: 147 meses de entrenamiento y 63 de prueba, de abril de 2021 a junio de 2026.",
      68:"RMSE de tres modelos simples reutilizados del Laboratorio 1; menor error es mejor.",
      69:"8 Observaciones y estimaciones LSTM del Laboratorio 2",
      70:"Dos líneas sobre el mismo eje temporal permiten localizar divergencias entre observación y estimación histórica. Azul sólido identifica valores observados y coral discontinuo las estimaciones. El usuario elige la serie total o América del Norte, consulta valores y usa zoom. Para la serie total, MAE es 74,090, RMSE 85,805 y sMAPE 34.4 %. Estas métricas se presentan aparte: no se asegura que el protocolo de ambos laboratorios sea equivalente. No se incluyen meses futuros ni intervalos nuevos de incertidumbre.",
      72:"Evaluación histórica LSTM de la serie total, conservada del avance.",
      74:"La tabla actualiza la planificación de cierre y conserva responsables por actividad. Los resultados indicados son entregables previstos; la verificación técnica se describe después de la tabla.",
      75:"Verificación de la versión final",
      76:"Se ejecutaron once pruebas automatizadas: continuidad y conservación de totales, agregaciones y cobertura parcial, referencia estacional, selección válida y fuera de filtro, procedencia de métricas, ocho vistas y tres modelos simples, escalas y filtros, consulta sin datos, selección de vistas y modelos, cambio de mes y consulta de mercados y LSTM. Todas pasaron. Además, en el navegador se seleccionó diciembre de 2014 en la serie y se comprobó el cambio del selector y del desglose por vía.",
      77:"La versión final cumple las ocho visualizaciones, la selección de vistas, el enlace serie-vías, los niveles de detalle y la comparación de modelos existentes. Los resultados describen registros académicos y su evaluación histórica. Se recomienda revisar la fuente y comparar meses equivalentes antes de usar variaciones para decisiones de gestión; el tablero no demuestra causas ni garantiza predicciones futuras.",
      79:"Equipo del proyecto. Base_Migracion_2009-2026jun.xlsx, hojas Datos y Notas. Copia original conservada en data/raw. Las cantidades filtradas reproducen la serie del avance.",
      80:"Equipo del proyecto. Laboratorio 1 Series de Tiempo. Exportación comparacion_modelos.csv y cuaderno laboratorio-1-series-tiempo.ipynb. El archivo data/raw/modelos_lab1.csv conserva las métricas usadas en la entrega final.",
      81:"Equipo del proyecto. Laboratorio 2. Predicciones y métricas LSTM conservadas en el avance del Laboratorio 10. Los informes de avance permanecen como referencia histórica."
    }
    for idx,texto in textos.items():cambiar(p[idx],texto)
    # Mantener el párrafo de modelos completo para evitar un salto a media frase.
    for idx,propiedad in [(66,'keepLines')]:
        pr=p[idx].find('w:pPr',NS)
        if pr is None:pr=E.SubElement(p[idx],W+'pPr')
        E.SubElement(pr,W+propiedad).set(W+'val','true')
    # Añadir tres bloques con los mismos encabezados, cuerpo, figuras y pies del avance.
    rel=E.fromstring(partes["word/_rels/document.xml.rels"])
    PR="{http://schemas.openxmlformats.org/package/2006/relationships}"
    def ajustar_imagen(parrafo,archivo,relacion=None):
        im=Image.open(archivo);razon=im.height/im.width
        if relacion:
            for b in parrafo.xpath('.//a:blip',namespaces=NS):b.set(R+'embed',relacion)
        for extent in parrafo.xpath('.//wp:extent|.//a:xfrm/a:ext',namespaces=NS):
            ancho=extent.get('cx');extent.set('cy',str(round(int(ancho)*razon)))
    imagenes={42:('image2.png','paleta.png'),47:('image3.png','bosquejo_interfaz.png'),55:('image4.png','evolucion_mensual.png'),59:('image5.png','vias_diciembre_2019.png'),63:('image6.png','indice_estacional.png'),67:('image7.png','comparacion_modelos.png'),71:('image8.png','prediccion_lstm.png')}
    for idx,(dest,archivo) in imagenes.items():
        partes['word/media/'+dest]=(ROOT/'figuras'/archivo).read_bytes();ajustar_imagen(p[idx],ROOT/'figuras'/archivo)
    nuevos=[
      ('3 Evolución por región de residencia','Las líneas muestran la trayectoria de las cuatro regiones con mayor flujo del periodo y agrupan el resto en Otras regiones para evitar una leyenda saturada. El usuario cambia años, meses y nivel temporal y oculta series con la leyenda. El selector regional restringe el ranking de países. Esta vista ayuda a revisar diferencias entre mercados; las categorías se conservan como aparecen en la fuente, sin atribuir causas.','regiones.png','Evolución regional con cuatro categorías principales y el resto agrupado.'),
      ('4 Países de residencia con mayor flujo','Las barras horizontales facilitan comparar cantidades y leer nombres largos. El ranking responde a los años, los meses, la región y la cantidad de países seleccionada entre 3 y 20. Los valores emergentes muestran cantidades exactas. Su utilidad es localizar mercados con mayor volumen, considerando el cambio de detalle por país desde 2023.','mercados.png','Ranking ilustrativo de países para toda la cobertura disponible.'),
      ('5 Puntos de ingreso con mayor flujo','El ranking de barras horizontales permite comparar puntos de acceso con etiquetas legibles. El usuario filtra la vía, los años y los meses y cambia la cantidad de fronteras mostradas. Si no hay registros se presenta un mensaje explícito. Esta vista permite revisar concentración de ingresos, sin equiparar falta de detalle o ceros registrados con ausencia de actividad.','fronteras.png','Ranking ilustrativo de fronteras con toda la cobertura disponible.')
    ]
    # Situar las vistas 3 a 5 antes de la estacionalidad, respetando la navegación.
    ancla=p[61]
    for i,(titulo,descripcion,archivo,pie) in enumerate(nuevos):
        bloques=[deepcopy(p[j]) for j in [57,58,59,60]]
        cambiar(bloques[0],titulo);cambiar(bloques[1],descripcion);cambiar(bloques[3],pie)
        rid=f'rId{19+i}';nombre=f'final_{i+1}.png'
        E.SubElement(rel,PR+'Relationship',Id=rid,Type=NS['r']+'/image',Target='media/'+nombre)
        ajustar_imagen(bloques[2],ROOT/'figuras'/archivo,rid)
        for q in bloques[2].xpath('.//wp:docPr',namespaces=NS):q.set('id',str(100+i));q.set('name',archivo);q.set('descr',pie)
        partes['word/media/'+nombre]=(ROOT/'figuras'/archivo).read_bytes()
        for b in bloques:ancla.addprevious(b)
    # Precisar la procedencia de las métricas sin sobrescribir la versión de avance.
    nota=deepcopy(p[15]);cambiar(nota,'Las métricas finales provienen de la exportación original del Lab 1 y difieren de las transcritas en el avance. Se conservan ambos archivos y se documenta la procedencia en codebook.md. La etiqueta Prophet - respaldo aditivo corresponde a un modelo alternativo usado cuando la biblioteca Prophet no estaba disponible. MAE es el error absoluto medio y RMSE penaliza más los errores grandes; ambos se expresan en visitantes. sMAPE expresa un error porcentual simétrico.');p[68].addnext(nota)
    tabla=body.find('w:tbl',NS)
    filas=tabla.findall('w:tr',NS)
    # Word necesita más ancho para el encabezado que el exportador del avance.
    # Mantener las cuatro columnas y evitar partir la palabra Responsable.
    for rpr in filas[0].findall('w:tc',NS)[1].xpath('.//w:rPr',namespaces=NS):
        for etiqueta in ['sz','szCs']:
            tam=rpr.find(W+etiqueta)
            if tam is None:tam=E.SubElement(rpr,W+etiqueta)
            tam.set(W+'val','18')
    actividades=[('24 oct.','Ihan','Organizar las fuentes y reproducir los agregados por mes, mercado, región y frontera.','Datos y auditoría'),('24 oct.','Diego','Completar filtros, niveles de detalle y el enlace entre serie y vías.','Interfaz completa'),('24 oct.','Milton','Revisar la paleta, el bosquejo y el contenido del avance.','Diseño de referencia'),('24 oct.','Ihan','Contrastar las métricas con la exportación del Laboratorio 1.','Resultados trazables'),('24 oct.','Diego','Integrar las ocho vistas y ejecutar las pruebas de interacción.','Aplicación verificada'),('24 oct.','Ihan y Diego','Actualizar el documento de diseño y exportar el PDF.','Informe final'),('25 oct.','Milton','Revisar etiquetas y limitaciones en la versión completa.','Revisión de contenido'),('25 oct.','Ihan','Comprobar la ejecución desde los archivos originales.','Reproducción del flujo'),('25 oct.','Diego','Probar la navegación y los filtros antes de enviar.','Revisión funcional'),('25 oct.','Todos','Verificar PDF y enlace del repositorio y realizar la entrega.','Entrega final')]
    for fila,datos in zip(filas[1:],actividades):
        for celda,texto in zip(fila.findall('w:tc',NS),datos):
            cambiar(celda.find('w:p',NS),texto)
    for texto in ['Menene. CC3084 Data Science 2026. Estructura de proyectos del curso. https://github.com/menene/cc3084-2026-02-40','Streamlit. st.plotly_chart y AppTest. https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart y https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest']:
        nuevo=deepcopy(p[81]);cambiar(nuevo,texto);body.insert(len(body)-1,nuevo)
    partes['word/document.xml']=E.tostring(doc,xml_declaration=True,encoding='UTF-8',standalone=True)
    partes['word/_rels/document.xml.rels']=E.tostring(rel,xml_declaration=True,encoding='UTF-8',standalone=True)
    ajustes=E.fromstring(partes['word/settings.xml']);update=ajustes.find(W+'updateFields')
    if update is None:update=E.SubElement(ajustes,W+'updateFields')
    update.set(W+'val','true');partes['word/settings.xml']=E.tostring(ajustes,xml_declaration=True,encoding='UTF-8',standalone=True)
    destino=ROOT/'work/informe_final.docx';destino.parent.mkdir(exist_ok=True)
    with ZipFile(destino,'w',ZIP_DEFLATED) as z:
        for nombre,contenido in partes.items():z.writestr(nombre,contenido)
    print(destino)


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plantilla', help='Plantilla externa opcional; por defecto se recupera del historial de Git.')
    generar(parser.parse_args().plantilla)
