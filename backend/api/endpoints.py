# api/endpoints.py
import sys
import os
from flask import Flask, jsonify, request, render_template, Response
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
    return Response(pre.getDashboardCliente(cliente), content_type="application/json")

@app.route("/contugas/dashboard", methods=['GET'])
def getDashboard():
    return render_template("dashboard.html")

if __name__ == '__main__':
    #pre.readDataExcel()
    #pre.processAnomalias()
    pre.saveDashboradClienteInCache()
    app.run(host="0.0.0.0", port=5000, debug=True)