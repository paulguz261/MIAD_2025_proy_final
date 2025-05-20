import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_DIR, "data")
DATA_DIR_RAW = os.path.join(DATA_DIR,"raw")
DATA_DIR_PROCESSED = os.path.join(DATA_DIR,"processed")
MODEL_DIR = os.path.join(PROJECT_DIR,"models")
DATA_DIR_PARQUET = os.path.join(DATA_DIR,"parquet")
DATA_DIR_PREDICTIONS_PARQUET = os.path.join(DATA_DIR,"parquet/predictions")
DATA_DIR_PROCESSED_PARQUET = os.path.join(DATA_DIR,"parquet/processed")

JOINED_FILE_NAME = "datos_unidos.csv"
PROCESSED_FILE_NAME = "datos_unidos_fechas.csv"
RAW_FILE_NAME = "Datos.xlsx"
PARQUET_PYSPARK_FILE_NAME = "{}_data.parquet"
MODEL_FILENAME = "{}_pipeline.pkl"
PARQUET_PREDICTIONS_CLIENT_FILE_NAME = "{}_prediction.parquet"
PARQUET_PROCESSED_CLIENT_FILE_NAME = "{}_processed.parquet"

DIR_JOINED_FILE = os.path.join(DATA_DIR_PROCESSED,JOINED_FILE_NAME)
DIR_PROCESSED_FILE = os.path.join(DATA_DIR_PROCESSED,PROCESSED_FILE_NAME)
DIR_RAW_FILE = os.path.join(DATA_DIR_RAW,RAW_FILE_NAME)
DIR_PARQUET_PYSPARK_FILE = os.path.join(DATA_DIR_PARQUET,PARQUET_PYSPARK_FILE_NAME)
DIR_MODELS_FILE = os.path.join(MODEL_DIR,MODEL_FILENAME)
DIR_PARQUET_CLIENT_PREDICTION_FILE = os.path.join(DATA_DIR_PREDICTIONS_PARQUET,PARQUET_PREDICTIONS_CLIENT_FILE_NAME)
DIR_PARQUET_CLIENT_PROCESSED_FILE = os.path.join(DATA_DIR_PROCESSED_PARQUET,PARQUET_PROCESSED_CLIENT_FILE_NAME)

INPUT_FILE = os.path.join(DATA_DIR, "datos_unidos.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "resultado_anomalias.csv")