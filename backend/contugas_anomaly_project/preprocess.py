import pandas as pd
import numpy as np

import os
import sys
# Agrega el directorio actual al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config as cnf

def readDataExcel():
    # Leer todas las hojas del archivo Excel
    excel_data = pd.read_excel(cnf.DIR_RAW_FILE, sheet_name=None, engine='openpyxl')
    for cliente, datos in excel_data.items():
        df_cliente = datos.copy()
        df_cliente["is_anomaly"] = np.random.rand(len(df_cliente))
        file_client_parquet_path = cnf.DIR_PARQUET_PYSPARK_FILE.format(cliente.lower())
        df_cliente.to_parquet(file_client_parquet_path, index=False)
        #print(datos.head())  # Muestra las primeras 5 filas de cada hoja
        #print("\n")
        
def readDataCliente(cliente):
    data_cliente_filename = cnf.DIR_PARQUET_PYSPARK_FILE.format(cliente.lower())
    df = pd.read_parquet(data_cliente_filename, engine='pyarrow')
    data = df.to_dict(orient="records")
    return data


def getAllClientes():
    return ["CLIENTE1", "CLIENTE2", "CLIENTE3", "CLIENTE4", "CLIENTE5", "CLIENTE6", "CLIENTE7", "CLIENTE8",
            "CLIENTE9", "CLIENTE10", "CLIENTE11", "CLIENTE12", "CLIENTE13", "CLIENTE14", "CLIENTE15",
            "CLIENTE16", "CLIENTE17", "CLIENTE18", "CLIENTE19", "CLIENTE20"]
        
def cargar_datos(file_path):
    """Cargar datos de csv"""
    df = pd.read_csv(file_path)
    df["Fecha"] = pd.to_datetime(df["Fecha"])
    return df

def carga_datos_raw():
    """ Carga los datos en .xlsx, une la informacion de las hojas en un unico DataFrame"""
    df = pd.read_excel(cnf.DIR_RAW_FILE, sheet_name=None)

    df_total = pd.concat(
        [df.assign(cliente=key) for key, df in df.items()],
        ignore_index=True
    )
    df_total.to_csv(cnf.DIR_JOINED_FILE, index=False)

    return True

def completar_fechas(df):
    """Completa las fechas faltantes para cada cliente"""
    # Crea el arreglo de fechas 
    start_date = df["Fecha"].min()
    end_date = df["Fecha"].max()

    datetime_list = pd.date_range(start=start_date, end=end_date, freq='h').to_list()
    df_datetime_list = pd.DataFrame(datetime_list ,columns=["Fecha"])

    # Une informacion de cada cliente con las fechas 
    arr_total_fecha = []
    for clt in df["cliente"].unique():
        fltr = df["cliente"] == clt
        df_temp = pd.merge(df_datetime_list,df[fltr], on="Fecha", how = "left")
        df_temp["cliente"] = clt
        arr_total_fecha.append(df_temp)

    df_total_fecha = pd.concat(arr_total_fecha)
    df_total_fecha.to_csv(cnf.DIR_PROCESSED_FILE, index=False)

    return True, df_total_fecha

def convierte_datos_raw_to_processed():
    """"Realiza la lectura de datos insumo y su procesamiento par auna base estandarizada"""
    valida = carga_datos_raw()
    df = cargar_datos(cnf.DIR_JOINED_FILE)
    valida, df_total_fecha = completar_fechas(df)

    return True

def preprocesa_datos(df):
    """Aplica las transformaciones a los datos."""
    df.fillna(0, inplace=True)

    # Temporal features
    df["hora"] = df["Fecha"].dt.hour
    df["dia_semana"] = df["Fecha"].dt.dayofweek
    df["mes"] = df["Fecha"].dt.month
    df["dia_del_mes"] = df["Fecha"].dt.day

    # Deltas
    df["delta_volumen"] = df.groupby("cliente")["Volumen"].diff()
    df["delta_presion"] = df.groupby("cliente")["Presion"].diff()
    df["delta_temperatura"] = df.groupby("cliente")["Temperatura"].diff()

    # Flags
    df["es_madrugada"] = df["hora"].between(0, 5).astype(int)
    df["es_fin_de_mes"] = df["Fecha"].dt.is_month_end.astype(int)

    df.fillna(0, inplace=True)

    return df