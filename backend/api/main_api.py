# main_api.py

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import pandas as pd
import joblib
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import contugas_anomaly_project.preprocess as pre
import contugas_anomaly_project.config as cnf
import contugas_anomaly_project.model as mdl

app = FastAPI()

# Allow frontend (JavaScript) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to your frontend later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/client-data")
def get_client_data(cliente: str):
    # Load the full dataset
    df = pre.cargar_datos(cnf.DIR_PROCESSED_FILE)
    
    # Filter by client
    df_cliente = df[df["cliente"] == cliente]

    # Preprocess it
    df_cliente = pre.preprocesa_datos(df_cliente)

    # Load the model
    model_path = os.path.join(cnf.MODEL_DIR,)
    model_path = f"{cliente}_pipeline.pkl"
    pipeline = joblib.load(model_path)

    # Predict anomalies
    df_result = mdl.predict_with_pipeline(pipeline, df_cliente)

    # Return only needed columns as JSON
    return df_result[["Fecha", "Presion", "Temperatura", "Volumen", "anomaly_label"]].to_dict(orient="records")
