import os

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(PROJECT_DIR, "data")
DATA_DIR_RAW = os.path.join(DATA_DIR,"raw")
DATA_DIR_PROCESSED = os.path.join(DATA_DIR,"processed")
MODEL_DIR = os.path.join(PROJECT_DIR,"models")

JOINED_FILE_NAME = "datos_unidos.csv"
PROCESSED_FILE_NAME = "datos_unidos_fechas.csv"
RAW_FILE_NAME = "Datos.xlsx"

DIR_JOINED_FILE = os.path.join(DATA_DIR_PROCESSED,JOINED_FILE_NAME)
DIR_PROCESSED_FILE = os.path.join(DATA_DIR_PROCESSED,PROCESSED_FILE_NAME)
DIR_RAW_FILE = os.path.join(DATA_DIR_RAW,RAW_FILE_NAME)

INPUT_FILE = os.path.join(DATA_DIR, "datos_unidos.csv")
OUTPUT_FILE = os.path.join(DATA_DIR, "resultado_anomalias.csv")