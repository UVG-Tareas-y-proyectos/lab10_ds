"""Ilustraciones del documento de diseño con los mismos datos del tablero."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pandas as pd
from src.preparar_datos import preparar

ROOT = Path(__file__).resolve().parents[1]
D = ROOT/"data/processed"
OUT = ROOT/"figuras"
C = ["#214E66", "#2A7F8E", "#6C7A59", "#615B84", "#7C8991"]


def generar():
    if not (D/"auditoria.json").exists():
        preparar()
    OUT.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family":"DejaVu Sans", "font.size":10})
    def guardar(fig, ax, nombre):
        ax.spines[["top","right"]].set_visible(False)
        ax.grid(axis="y",color="#dddddd",linewidth=.6)
        ax.set_axisbelow(True)
        fig.tight_layout()
        fig.savefig(OUT/nombre,dpi=180,bbox_inches="tight")
        plt.close(fig)
    m = pd.read_csv(D/"serie_mensual_total.csv",parse_dates=["fecha"])
    fig,ax=plt.subplots(figsize=(10.5,4.5))
    ax.plot(m.fecha,m.viajeros/1000,color=C[0],linewidth=1.8)
    ax.axvspan(pd.Timestamp('2020-03-01'),pd.Timestamp('2021-12-31'),color='#C96B4B',alpha=.12,label='Periodo atípico 2020–2021')
    ax.set(xlabel='Mes',ylabel='Ingresos de visitantes (miles)');ax.legend(frameon=False)
    guardar(fig,ax,'evolucion_mensual.png')
    v=pd.read_csv(D/'serie_mensual_por_via.csv',parse_dates=['fecha'])
    fila=v[v.fecha.eq('2019-12-01')].iloc[0]
    fig,ax=plt.subplots(figsize=(8.8,4.4));ax.bar(['Aérea','Marítima','Terrestre'],fila.iloc[1:].astype(float)/1000,color=C[:3]);ax.set_ylabel('Ingresos de visitantes (miles)')
    guardar(fig,ax,'vias_diciembre_2019.png')
    e=pd.read_csv(D/'indice_estacional.csv')
    fig,ax=plt.subplots(figsize=(9.5,4.4));ax.bar(['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'],e.indice_estacional,color=C[1]);ax.axhline(100,color=C[-1],linestyle='--');ax.set_ylabel('Índice estacional (referencia = 100)')
    guardar(fig,ax,'indice_estacional.png')
    modelos=pd.read_csv(D/'metricas_modelos.csv')
    modelos=modelos[modelos.modelo.isin(['Suavizamiento exponencial simple','Holt-Winters aditivo','Seasonal naive'])].sort_values('rmse',ascending=False)
    fig,ax=plt.subplots(figsize=(10.5,4.4));ax.barh(modelos.modelo,modelos.rmse/1000,color=C[-1]);ax.set_xlabel('RMSE de prueba (miles de visitantes; menor es mejor)')
    guardar(fig,ax,'comparacion_modelos.png')
    p=pd.read_csv(D/'predicciones_lstm.csv',parse_dates=['fecha']);p=p[p.clave.eq('total_viajeros')]
    fig,ax=plt.subplots(figsize=(10.5,4.5));ax.plot(p.fecha,p.real/1000,label='Observado',color=C[0]);ax.plot(p.fecha,p.prediccion/1000,label='Estimado LSTM',color='#C96B4B',linestyle='--');ax.set(xlabel='Mes de prueba histórica',ylabel='Ingresos de visitantes (miles)');ax.legend(frameon=False)
    guardar(fig,ax,'prediccion_lstm.png')
    for archivo,col,nombre,color in [('mercados','País','mercados.png',C[1]),('fronteras','Frontera','fronteras.png',C[2])]:
        g=pd.read_csv(D/f'{archivo}.csv').groupby(col).viajeros.sum().nlargest(8).sort_values()
        fig,ax=plt.subplots(figsize=(10.5,4.5));ax.barh(g.index,g.values/1e6,color=color);ax.set_xlabel('Ingresos acumulados 2009–junio 2026 (millones)')
        guardar(fig,ax,nombre)
    r=pd.read_csv(D/'regiones.csv',parse_dates=['fecha']);grandes=r.groupby('Región').viajeros.sum().nlargest(4).index
    r['Región']=r['Región'].where(r['Región'].isin(grandes),'Otras regiones');r=r.groupby(['fecha','Región']).viajeros.sum().reset_index()
    fig,ax=plt.subplots(figsize=(10.5,4.5))
    for i,(nombre,parte) in enumerate(r.groupby('Región')):ax.plot(parte.fecha,parte.viajeros/1000,label=nombre.title(),color=C[i],linestyle='--' if nombre=='Otras regiones' else '-')
    ax.set(xlabel='Mes',ylabel='Ingresos de visitantes (miles)');ax.legend(frameon=False,fontsize=8,ncol=2)
    guardar(fig,ax,'regiones.png')
    fig,ax=plt.subplots(figsize=(10.2,2.5));ax.set(xlim=(0,5),ylim=(0,1));ax.axis('off')
    for i,(nombre,codigo,uso) in enumerate([('Azul','#214E66','Observaciones'),('Turquesa','#2A7F8E','Comparaciones'),('Ocre','#D7A84B','Referencia'),('Coral','#C96B4B','Estimaciones y alertas'),('Verde','#6C7A59','Vía terrestre')]):
        ax.add_patch(Rectangle((i+.08,.43),.84,.45,color=codigo));ax.text(i+.5,.31,nombre,ha='center');ax.text(i+.5,.19,codigo,ha='center',fontsize=8);ax.text(i+.5,.06,uso,ha='center',fontsize=7.5)
    fig.savefig(OUT/'paleta.png',dpi=180,bbox_inches='tight');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.2,5));ax.set(xlim=(0,10),ylim=(0,5));ax.axis('off')
    def caja(x,y,w,h,text):
        ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='#666666'));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
    caja(.1,.1,1.8,4.8,'Controles\n\nAños y meses\n\nDetalle temporal\n\nGráficas visibles')
    caja(2,4,7.9,.9,'Observatorio del flujo turístico a Guatemala\nIndicadores del periodo consultado')
    caja(2,3.4,7.9,.45,'Exploración  |  Mercados y acceso  |  Estacionalidad y modelos  |  Metodología')
    caja(2,1.9,3.8,1.3,'1 Evolución temporal\nClic en un punto → mes de detalle');caja(6,1.9,3.9,1.3,'2 Desglose por vía\nActualiza con el mes seleccionado')
    caja(2,.9,7.9,.8,'3 Regiones   4 Países   5 Fronteras\nFiltros de región y vía, cantidad de resultados')
    caja(2,.1,7.9,.6,'6 Estacionalidad   7 Error de modelos   8 Observado y LSTM\nMetodología y descargas')
    fig.savefig(OUT/'bosquejo_interfaz.png',dpi=180,bbox_inches='tight');plt.close(fig)


if __name__=='__main__':
    generar()
