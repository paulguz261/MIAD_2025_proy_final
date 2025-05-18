# main_api.py

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import sys
import pandas as pd
import joblib
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from contugas_anomaly_project import config as cnf
from contugas_anomaly_project import model2604
from contugas_anomaly_project import preprocess as pre
from contugas_anomaly_project import model as mdl
from data.clientes import get_all_clientes
from datetime import datetime
import json
 
# Obtener la ruta absoluta a la carpeta 'templates' fuera de 'backend/api'
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))

# Crear la instancia de Flask y especificar la carpeta de plantillas
app = Flask(__name__, template_folder=template_dir)
# Allow frontend (JavaScript) to connect
CORS(app) 

@app.route("/api/client-data", methods=['GET'])
def get_client_data():
    cliente = request.args.get('cliente')
    # Load the full dataset
    df = pre.cargar_datos(cnf.DIR_PROCESSED_FILE)
    
    # Filter by client
    df_cliente = df[df["cliente"] == cliente]

    # Preprocess it
    df_cliente = pre.preprocesa_datos(df_cliente)

    # Load the model
    model_path = os.path.join(cnf.MODEL_DIR, f"{cliente}_pipeline.pkl")
    pipeline = joblib.load(model_path)

    # Predict anomalies
    df_result = mdl.predict_with_pipeline(pipeline, df_cliente)
    
    return jsonify({"resultados":df_result[["Fecha", "Presion", "Temperatura", "Volumen", "anomaly_label"]].to_dict(orient="records")})


# Función para cargar el modelo
def load_model(cliente):
    model_path = os.path.join(cnf.MODEL_DIR, f"{cliente}_pipeline.pkl")
    model = joblib.load(model_path)
    return model

@app.route('/api/predict', methods=['GET'])
def predict():
    # Recibimos los parámetros de la URL
    fecha = request.args.get('fecha')  # "2023-12-31 19:00:00"
    presion = request.args.get('presion')  # Ejemplo: 1015
    temperatura = request.args.get('temperatura')  # Ejemplo: 25
    volumen = request.args.get('volumen')  # Ejemplo: 500
    cliente = request.args.get('cliente', 'CLIENTE1')  # Si no se pasa, tomamos 'CLIENTE1' por defecto

    # Load the full dataset
    df = pre.cargar_datos(cnf.DIR_PROCESSED_FILE)
    
    # Filter by client
    df_cliente = df[df["cliente"] == cliente]
    nuevo = pd.DataFrame([{'Fecha': pd.to_datetime(fecha), 'Presion': float(presion), 'Temperatura': float(temperatura), 'Volumen': float(volumen), 'cliente': cliente}])
    df_cliente = pd.concat([df_cliente, nuevo], ignore_index=True)
    # Preprocess it
    df_cliente = pre.preprocesa_datos(df_cliente)

    # Load the model
    model_path = os.path.join(cnf.MODEL_DIR, f"{cliente}_pipeline.pkl")
    pipeline = joblib.load(model_path)

    # Predict anomalies
    df_result = mdl.predict_with_pipeline(pipeline, df_cliente)
    
    #return jsonify({"resultados":df_result[["Fecha", "Presion", "Temperatura", "Volumen", "anomaly_label"]].to_dict(orient="records")})
    clientes = get_all_clientes()
    return render_template("dashboard_v1.html", clientes=clientes)

@app.route("/", methods=["GET"])
def index():
    return render_template("dashboard.html")

@app.route("/v1", methods=["GET"])
def indexV1():
    clientes = get_all_clientes()
    return render_template("dashboard_v1.html", clientes=clientes)

@app.route("/v2", methods=["GET"])
def indexV2():
    return render_template("dashboard_v2.html")

@app.route("/v3", methods=["GET"])
def indexV3():
    clientes = get_all_clientes()
    return render_template("dashboard_v1.html", clientes=clientes, grafico_html=model2604.proccessData())
    
@app.route("/scatter", methods=["GET"])
def indexScatter():
    return render_template("scatter.html")

@app.route("/api/save-data", methods=['GET'])
def sava_data():
    model_path = os.path.join(cnf.DIR_PARQUET_PYSPARK_FILE, "data_prueba.parquet")
    df = pd.DataFrame({
    'nombre': ['Ana', 'Luis', 'Carlos'],
    'edad': [25, 30, 35]
    })

    # Guardar como archivo Parquet
    df.to_parquet(model_path, engine='pyarrow', index=False)
    
    return jsonify({"response":"saved"})

@app.route("/api/get-data", methods=['GET'])
def get_parquet_data():
    model_path = os.path.join(cnf.DIR_PARQUET_PYSPARK_FILE, "data_prueba.parquet")
    df = pd.read_parquet(model_path, engine='pyarrow')
    data = df.to_dict(orient="records")

    # Envolver en un diccionario (por ejemplo, para enviar como respuesta API)
    response = {"response": data}

    # Convertir a JSON final
    json_str = json.dumps(response)

    return json_str


@app.route("/api/update-data", methods=['GET'])
def update_parquet_data():
    model_path = os.path.join(cnf.DIR_PARQUET_PYSPARK_FILE, "data_prueba.parquet")
    df = pd.read_parquet(model_path, engine='pyarrow')

    # 2. Crear el nuevo registro (como diccionario)
    nuevo_registro = {
        "nombre": "María",
        "edad": 28
    }

    # 3. Agregarlo al DataFrame
    df = pd.concat([df, pd.DataFrame([nuevo_registro])], ignore_index=True)

    # 4. Guardar el DataFrame actualizado nuevamente en Parquet
    df.to_parquet(model_path, index=False)
    return jsonify({"response":"updated"})


@app.route("/api-save-client/client-data", methods=['GET'])
def get_client_data_v222():
    cliente = request.args.get('cliente')
    df = pre.cargar_datos(cnf.DIR_PROCESSED_FILE)
    # Filter by client
    df_cliente = df[df["cliente"] == cliente]
    print(df_cliente.head())
    
    file_client_parquet_path = os.path.join(cnf.DIR_PARQUET_PYSPARK_FILE, f"{cliente}_data_consumo.parquet")
    # 4. Guardar el DataFrame actualizado nuevamente en Parquet
    df_cliente.to_parquet(file_client_parquet_path, index=False)
    
    return jsonify({"response":"save  data client"})


if __name__ == '__main__':
    app.run(debug=True)
    pre.save_in_parquet_files()
    
    
    