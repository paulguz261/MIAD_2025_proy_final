import os
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import contugas_anomaly_project.config as cnf
import contugas_anomaly_project.preprocess as pre

# Features used for training and inference
FEATURES = [
    "Presion", "Temperatura", "Volumen",
    "hora", "dia_semana", "mes", "dia_del_mes",
    "delta_volumen", "delta_presion", "delta_temperatura",
    "es_madrugada", "es_fin_de_mes"
]

def create_pipeline():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("iforest", IsolationForest(n_estimators=100, contamination='auto', random_state=42))
    ])

def fit_pipeline(df_client):
    df = df_client.copy()
    df = pre.preprocesa_datos(df)
    X=df[FEATURES]
    
    pipeline = create_pipeline()
    pipeline.fit(X)
    return pipeline

def save_pipeline(pipeline, cliente_name):
    
    model_path = os.path.join(cnf.MODEL_DIR, f"{cliente_name}_pipeline.pkl")
    joblib.dump(pipeline, model_path)
    return True

def train_pipeline_for_client(df_client, cliente_name, model_dir="models"):
    pipeline = fit_pipeline(df_client)
    save_pipeline(pipeline, cliente_name)
    return True

def train_all_clients():
    # pre.convierte_datos_raw_to_processed()
    df_insumo = pre.cargar_datos(cnf.DIR_PROCESSED_FILE)
    for cliente in df_insumo["cliente"].unique():
        df_cliente = df_insumo[df_insumo["cliente"] == cliente]
        validation = train_pipeline_for_client(df_cliente, cliente)
    return True


def predict_with_pipeline(pipeline, df_client):
    df = df_client.copy()
    X = df[FEATURES].fillna(0)
    df["anomaly_score"] = pipeline.decision_function(X)
    df["anomaly_label"] = pipeline.predict(X)
    df["anomaly_label"] = df["anomaly_label"].map({1: "normal", -1: "anomalía"})
    
    # Clasificar severidad
    q01 = df['anomaly_score'].quantile(0.01)
    q05 = df['anomaly_score'].quantile(0.05)

    def clasificar_severidad(score):
        if score < q01:
            return 'alta'
        elif score < q05:
            return 'media'
        else:
            return 'leve'

    df['nivel_anomalia_iforest'] = df['anomaly_score'].apply(clasificar_severidad)
    
    return df


train_all_clients()