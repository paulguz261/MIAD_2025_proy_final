import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from prophet import Prophet
from contugas_anomaly_project import config as cnf
from pyspark.sql import SparkSession
import mpld3

def createSparkSession():
    spark = SparkSession.builder \
        .appName("GuardarParquetApp") \
        .getOrCreate()
    return spark

def readAllClients():
    # Carga el archivo Excel con todas las hojas
    xls = pd.ExcelFile(cnf.DIR_RAW_FILE)
    sheet_names = xls.sheet_names  # nombres de las hojas

    # Cargar cada hoja como DataFrame y asignarle nombre cliente1, cliente2, ...
    clientes = {}
    data = pd.DataFrame(columns=['Fecha', 'Presion', 'Temperatura', 'Volumen', 'Cliente'])
    for i, nombre_hoja in enumerate(sheet_names):
        df = xls.parse(nombre_hoja)
        df['Cliente'] = nombre_hoja
        data = pd.concat([data, df], ignore_index=True)

    return data
    
def proccessData():
    #sparkSession = createSparkSession()
    data = readAllClients()
    #df_spark = sparkSession.createDataFrame(data)
    #df_spark.write.parquet(cnf.DIR_PARQUET_PYSPARK_FILE)
    
    # -----------------------------
    # 1. Seleccionar cliente y variable
    # -----------------------------
    cliente_id = 'CLIENTE1'         # ← Cambia esto por el cliente que quieras analizar
    variable = 'Presion'            # ← Cambia esto por 'Temperatura' o 'Volumen' si querés
    df = data[data['Cliente'] > cliente_id]
    df = df.drop('Cliente', axis=1)
    serie = df[['Fecha', variable]].dropna().reset_index(drop=True)

    # ----------------------------------
    # 2. Modelo 1: Z-Score
    # ----------------------------------
    mean = serie[variable].mean()
    std = serie[variable].std()
    serie['zscore'] = (serie[variable] - mean) / std
    serie['zscore_anomaly'] = serie['zscore'].abs() > 3

    # ----------------------------------
    # 3. Modelo 2: Rolling Window
    # ----------------------------------
    window = 20
    serie['media_rol'] = serie[variable].rolling(window).mean()
    serie['std_rol'] = serie[variable].rolling(window).std()
    serie['upper'] = serie['media_rol'] + 3 * serie['std_rol']
    serie['lower'] = serie['media_rol'] - 3 * serie['std_rol']
    serie['rolling_anomaly'] = (serie[variable] > serie['upper']) | (serie[variable] < serie['lower'])

    # ----------------------------------
    # 4. Modelo 3: Isolation Forest
    # ----------------------------------
    model = IsolationForest(contamination=0.01, random_state=42)
    serie['iso_anomaly'] = model.fit_predict(serie[[variable]])
    serie['iso_anomaly'] = serie['iso_anomaly'] == -1


    print(serie.head())
    # ----------------------------------
    # 5. Visualización comparativa
    # ----------------------------------
    plt.figure(figsize=(15, 7))
    plt.plot(serie['Fecha'], serie[variable], label='Datos', color='blue')

    # Anomalías de cada modelo
    plt.scatter(serie['Fecha'][serie['zscore_anomaly']], serie[variable][serie['zscore_anomaly']],
                label='Z-Score', color='orange', marker='o')
    plt.scatter(serie['Fecha'][serie['rolling_anomaly']], serie[variable][serie['rolling_anomaly']],
                label='Rolling Window', color='green', marker='x')
    plt.scatter(serie['Fecha'][serie['iso_anomaly']], serie[variable][serie['iso_anomaly']],
                label='Isolation Forest', color='red', marker='*')

    plt.title(f'Comparación de métodos de detección de anomalías\nCliente: {cliente_id} | Variable: {variable}')
    plt.xlabel('Fecha')
    plt.ylabel(variable)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # Convertir la gráfica a HTML usando mpld3
    html_grafica = mpld3.fig_to_html(plt.gcf())

    # Limpiar la figura
    plt.close()

    return html_grafica

    
    
#proccessData()

import importlib.metadata

# Lista de librerías a verificar
libraries = [
    'pandas', 'numpy', 'matplotlib', 'scikit-learn', 'prophet', 'pyspark'
]

# Obtener la versión de cada librería
for lib in libraries:
    try:
        version = importlib.metadata.version(lib)
        print(f'{lib}: {version}')
    except importlib.metadata.PackageNotFoundError:
        print(f'{lib} no está instalada.')