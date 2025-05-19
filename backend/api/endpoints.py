# api/endpoints.py
import sys
import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.database import SessionLocal, Medicion, get_db
from typing import Optional, List
from datetime import datetime
import pandas as pd
import joblib
from pathlib import Path
from models.isolation_model import IsolationForestWithSeverity
from services.preprocessing import create_diff_variables
from contugas_anomaly_project import preprocess as pre



router = APIRouter()
# Crear la instancia de Flask y especificar la carpeta de plantillas
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static'))
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
# Allow frontend (JavaScript) to connect
CORS(app)

@router.get("/test")
def test_db(db: Session = Depends(get_db)):
    data = db.query(Medicion).count()
    return {"data": [data]}

@app.route("/api/clientes", methods=['GET'])
def obtener_clientes():
    return {"clientes": pre.getAllClientes()}

@app.route("/api/mediciones/<cliente>", methods=['GET'])
def obtener_mediciones(
    cliente: str
):
    data_cliente = pre.readDataCliente(cliente)
    if not data_cliente:
        raise HTTPException(status_code=404, detail="No se encontraron mediciones")
    output = [
        {
            "fecha": m['Fecha'],
            "presion": m['Presion'],
            "temperatura": m['Temperatura'],
            "volumen": m['Volumen'],
        }
        for m in data_cliente
    ]
    return jsonify(output)


@router.get("/clientes/{cliente}/rango-fechas")
def rango_fechas(cliente: str, db: Session = Depends(get_db)):
    min_fecha = (
        db.query(func.min(Medicion.fecha))
        .filter(func.lower(func.trim(Medicion.cliente)) == cliente.lower())
        .scalar()
    )
    max_fecha = (
        db.query(func.max(Medicion.fecha))
        .filter(func.lower(func.trim(Medicion.cliente)) == cliente.lower())
        .scalar()
    )
    return {"min_fecha": min_fecha, "max_fecha": max_fecha}


@app.route("/api/anomalias/<cliente>", methods=['GET'])
def obtener_anomalias(
    cliente: str
):
    data_cliente = pre.readDataCliente(cliente)
    data_cliente = pd.DataFrame(data_cliente)
    
    # 2. Cargar modelo correspondiente

    base_dir = Path(__file__).resolve().parent.parent
    modelo_path = base_dir / "models" / f"{cliente}_pipeline.pkl"
    if not modelo_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró el modelo para {cliente}")

    modelo = joblib.load(modelo_path)
    # Preprocesar datos
    data_cliente = create_diff_variables(data_cliente)
    print(data_cliente.head())
    # df = df.dropna()
    # 3. Aplicar el modelo
    X = data_cliente[['Presion', 'Temperatura', 'Volumen','delta_volumen','delta_presion','delta_temperatura']]
    X = X.dropna()
    predicciones = modelo.predict_severity(X) 

    data_cliente["criticidad"] = predicciones

    # 4. Filtrar anomalías y formatear
    anomalias = data_cliente[data_cliente["criticidad"] != "normal"]
    print("🔍 Cantidad de anomalías:", len(anomalias))
    # print(anomalias.head().to_dict())
    print(anomalias.isna().sum())
    anomalias = anomalias.fillna(value='normal')
    resultado = []
    for i, row in anomalias.iterrows():
        for var in ["Presion", "Temperatura", "Volumen"]:
            resultado.append({
                "fecha": row["Fecha"],
                "variable": var,
                "valor": row[var],
                "criticidad": row["criticidad"]
            })
    return jsonify(resultado)   

@app.route("/contugas/dashboard", methods=['GET'])
def getDashboard():
    return render_template("dashboard.html")

if __name__ == '__main__':
    #pre.readDataExcel()
    app.run(debug=True)