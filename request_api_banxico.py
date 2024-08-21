# Importando las librerías necesarias
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import datetime  # Importa datetime
import creds  

# Función para obtener datos de la API de Banxico
def obtener_datos(tipo_cambio_serie, fecha_inicio, fecha_fin, token):
    url_base = f'https://www.banxico.org.mx/SieAPIRest/service/v1/series/{tipo_cambio_serie}/datos/{fecha_inicio}/{fecha_fin}'
    headers = {'Bmx-Token': token}
    response = requests.get(url_base, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return None

# Serie del tipo de cambio FIX
serie = 'SF43718' # Serie del tipo de cambio FIX

# Obtener la fecha corriente
fecha_actual = datetime.now().strftime('%Y-%m-%d')  

# Fechas de los sexenios, utilizando la fecha actual para el fin la fecha corriente
fechas = {
    "PAN": ("2006-12-01", "2012-11-30"), # Felipe Calderón Hinojosa
    "PRI": ("2012-12-01", "2018-11-30"), # Enrique Peña Nieto
    "MORENA": ("2018-12-01", fecha_actual)  # Andres Manuel Lopez Obrador, Fecha actual
}

# Obtener los datos para cada periodo
datos_sexenios = {}
for partido, (inicio, fin) in fechas.items():
    datos = obtener_datos(serie, inicio, fin, creds.token) 
    if datos:
        fechas_datos = [dato['fecha'] for dato in datos['bmx']['series'][0]['datos']]
        valores_datos = [float(dato['dato']) for dato in datos['bmx']['series'][0]['datos']]
        df = pd.DataFrame({'Fecha': pd.to_datetime(fechas_datos, format='%d/%m/%Y'), 'Tipo de Cambio': valores_datos})
        datos_sexenios[partido] = df

# Crear la gráfica
plt.figure(figsize=(14, 8))

# Colores para cada sexenio
colores = {
    "PAN": 'blue',
    "PRI": 'green',
    "MORENA": 'red'
}

# Graficar los datos
for partido, df in datos_sexenios.items():
    plt.plot(df['Fecha'], df['Tipo de Cambio'], label=partido, color=colores[partido])

# Sombrear los sexenios
plt.axvspan(pd.to_datetime("2006-12-01"), pd.to_datetime("2012-11-30"), color='blue', alpha=0.1)
plt.axvspan(pd.to_datetime("2012-12-01"), pd.to_datetime("2018-11-30"), color='green', alpha=0.1)
plt.axvspan(pd.to_datetime("2018-12-01"), pd.to_datetime(fecha_actual), color='red', alpha=0.1)

# Añadir líneas verticales para marcar cambios de gobierno
fechas_cambio = {
    "Continuación PAN": "2006-12-01",
    "Inicio PRI": "2012-12-01",
    "Inicio MORENA": "2018-12-01"
}

for evento, fecha in fechas_cambio.items():
    plt.axvline(pd.to_datetime(fecha), color='black', linestyle='--', linewidth=1)
    plt.text(pd.to_datetime(fecha), 22 , evento, rotation=90, horizontalalignment='center', color='black', fontsize=10)

# Añadir anotaciones en puntos clave
eventos = {
    "Crisis 2008": ("2008-10-10", 13.5),
    "Reformas Estructurales": ("2014-01-01", 13.0),
    "Inicio Pandemia COVID-19": ("2020-03-20", 24.0)
}

for evento, (fecha, valor) in eventos.items():
    plt.annotate(evento, xy=(pd.to_datetime(fecha), valor), xytext=(10, 50),
                 textcoords='offset points', arrowprops=dict(facecolor='black', shrink=0.05))

# Añadir una línea horizontal como referencia del tipo de cambio al final del sexenio de Calderón
valor_pan_final = datos_sexenios["PAN"]['Tipo de Cambio'].iloc[-1]
plt.axhline(valor_pan_final, color='blue', linestyle='--', label='Tipo de Cambio al final del sexenio del PAN')

# Estilo de gráfica
plt.style.use('ggplot')  # Cambiado a un estilo disponible

# Formatear el eje Y con el símbolo de moneda
plt.gca().yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.2f} MXN"))

# Añadir detalles a la gráfica
plt.title(f'Tipo de Cambio (FIX) durante los ultimos 3 sexenios\n'
          f'(01-12-2006 - Actualidad)', fontsize=14)
plt.figtext(0.13, 0.01, "Fuente de datos: Banco de México (Banxico) - API REST\n" "Creado por: Francisco Javier García García",            
            ha="left", fontsize=10)
plt.xlabel('Fecha', fontsize=12)
plt.ylabel('Tipo de Cambio (MXN por USD)', fontsize=12)
plt.legend(title="Partidos Politicos y Eventos Clave", loc="best", fontsize=10)
plt.grid(True)
plt.show()
