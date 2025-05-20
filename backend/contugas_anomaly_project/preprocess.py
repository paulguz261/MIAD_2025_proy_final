import pandas as pd
import numpy as np
import joblib
import os
import sys
# Agrega el directorio actual al sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config as cnf
from services.preprocessing import create_diff_variables
import orjson

data_cache = {}

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
        
        
        
        
        
def processAnomalias():
    for cliente in getAllClientes():
        data_cliente = readDataCliente(cliente)
        data_cliente = pd.DataFrame(data_cliente)
        # 2. Cargar modelo correspondiente
        modelo = joblib.load(cnf.DIR_MODELS_FILE.format(cliente.upper()))
        # Preprocesar datos
        data_cliente = create_diff_variables(data_cliente)
        # df = df.dropna()
        # 3. Aplicar el modelo
        X = data_cliente[['Presion', 'Temperatura', 'Volumen','delta_volumen','delta_presion','delta_temperatura']]
        X = X.dropna()
        predicciones = modelo.predict_severity(X) 

        data_cliente["criticidad"] = predicciones

        # 4. Filtrar anomalías y formatear
        print(data_cliente.head())
        anomalias = data_cliente[data_cliente["criticidad"] != "normal"]
        # print(anomalias.head().to_dict())
        anomalias = anomalias.fillna(value='normal')
        summary =  anomalias.drop(columns=["is_anomaly", "delta_volumen", "delta_presion", "delta_temperatura"])
        #print(anomalias)
        summary.to_parquet(cnf.DIR_PARQUET_CLIENT_PROCESSED_FILE.format(cliente.lower()), index=False)
        resultado = []
        for i, row in anomalias.iterrows():
            for var in ["Presion", "Temperatura", "Volumen"]:
                resultado.append({
                    "fecha": row["Fecha"],
                    "variable": var,
                    "valor": row[var],
                    "criticidad": row["criticidad"]
                })
        resultado = pd.DataFrame(resultado)
        resultado.to_parquet(cnf.DIR_PARQUET_CLIENT_PREDICTION_FILE.format(cliente.lower()), index=False)

def getAnomaliasCliente(cliente):
    anomalias_data = cnf.DIR_PARQUET_CLIENT_PROCESSED_FILE.format(cliente.lower())
    anomalias_splitted = cnf.DIR_PARQUET_CLIENT_PREDICTION_FILE.format(cliente.lower())
    df = pd.read_parquet(anomalias_splitted, engine='pyarrow')
    df_anomalias_data = pd.read_parquet(anomalias_data, engine='pyarrow')
    #print(df.head())
    df_anomalias_data = df_anomalias_data.sort_values(by="Fecha", ascending=False)
    df_anomalias_data['Fecha'] = df_anomalias_data["Fecha"].dt.strftime("%d/%m/%Y %H:%M:%S")
    
    response = {}
    response['data'] = df_anomalias_data.to_dict(orient="records")
    response['presion'] = filterData(df, 'Presion')
    response['volumen'] = filterData(df, 'Volumen')
    response['temperatura'] = filterData(df, 'Temperatura')
    return response         

def filterData(data, variable):
    df_filtered = data[data["variable"] == variable]
    df_filtered['fecha'] = df_filtered["fecha"].dt.strftime("%d/%m/%Y %H:%M:%S")
    response_temp =  {}
    response_temp['data']=df_filtered.to_dict(orient="list")
    response_temp['data_points'] = filterCriticidad(df_filtered)
    response_temp['average'] = float(round(np.mean(response_temp['data']['valor']), 2))
    return response_temp

def filterCriticidad(data):
    response = {}
    for criticidad in getCriticidades():
        dataByCriticidad = data[data["criticidad"] == criticidad]
        response[criticidad] = [{"x": row["fecha"], "y": row["valor"]}
            for _, row in dataByCriticidad.iterrows()
        ]
    return response

def saveDashboradClienteInCache():
    for cliente in getAllClientes():
        data_cache[cliente] = orjson.dumps(getAnomaliasCliente(cliente))
        
def getDashboardCliente(cliente):
    return data_cache[cliente]


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

def getCriticidades():
    return ["alta", "media", "leve"]