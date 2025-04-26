# main_api.py

from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import os
import sys
import pandas as pd
import joblib
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import contugas_anomaly_project.preprocess as pre
import contugas_anomaly_project.config as cnf
import contugas_anomaly_project.model as mdl
from data.clientes import get_all_clientes
from datetime import datetime
import plotly.graph_objs as go
import plotly.io as pio
 
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
    return render_template("dashboard_v1.html", clientes=clientes, grafico_html=grafico(df_result))

@app.route("/", methods=["GET"])
def index():
    return render_template("dashboard.html")

@app.route("/v1", methods=["GET"])
def indexV1():
    clientes = get_all_clientes()
    return render_template("dashboard_v1.html", clientes=clientes, grafico_html=grafico())

@app.route("/v2", methods=["GET"])
def indexV2():
    return render_template("dashboard_v2.html")

def grafico(data):
  
    # Crear la figura con varias líneas
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Fecha'], y=data['Presion'], mode='lines+markers', name='Presión'))
    fig.add_trace(go.Scatter(x=data['Fecha'], y=data['Temperatura'], mode='lines+markers', name='Temperatura'))
    fig.add_trace(go.Scatter(x=data['Fecha'], y=data['Volumen'], mode='lines+markers', name='Volumen'))

    fig.update_layout(title="Presión, Temperatura y Volumen a lo largo del tiempo",
                      xaxis_title="Fecha",
                      yaxis_title="Valor",
                      legend_title="Variables")

    # Convertir el gráfico a HTML
    return pio.to_html(fig, full_html=False)
    
if __name__ == '__main__':
    app.run(debug=True)