# db/init_data.py
import pandas as pd
import os
from sqlalchemy.orm import Session
from database import engine, Medicion
from datetime import datetime
from tqdm import tqdm

# Ruta del archivo CSV (ajusta si cambia)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "datos_unidos_fechas.csv")

def cargar_datos():
    df = pd.read_csv(CSV_PATH)
    print(f"Cantidad datos en la base {len(df)}")
    df = pd.read_csv(CSV_PATH, parse_dates=["Fecha"])
    print(f"Cantidad datos en la base {len(df)}")

    # Limpieza mínima (opcional)
    df.dropna(subset=["Fecha", "Presion", "Temperatura", "Volumen", "cliente"], inplace=True)

    # Convertimos el DataFrame en una lista de objetos Medicion
    registros = []
    for _, row in tqdm(df.iterrows(), total=len(df)):
        registros.append(Medicion(
            cliente=row["cliente"],
            fecha=row["Fecha"],
            presion=row["Presion"],
            temperatura=row["Temperatura"],
            volumen=row["Volumen"]
        ))

    with Session(engine) as session:
        # limpiar la tabla antes de cargar nuevos datos
        session.query(Medicion).delete()
        session.commit()

        # Guardar los registros en la base de datos
        session.bulk_save_objects(registros)
        session.commit()

if __name__ == "__main__":
    cargar_datos()
    print("✅ Datos cargados en la base de datos")
