# api/endpoints.py
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


router = APIRouter()


@router.get("/test")
def test_db(db: Session = Depends(get_db)):
    data = db.query(Medicion).count()
    return {"data": [data]}

@router.get("/clientes")
def obtener_clientes(db: Session = Depends(get_db)):
    clientes = db.query(Medicion.cliente).distinct().all()
    return [c[0] for c in clientes if c[0]]

@router.get("/mediciones/{cliente}")
def obtener_mediciones(
    cliente: str,
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(1000, ge=1, le=10000)
):
    db: Session = SessionLocal()
    query = db.query(Medicion).filter(Medicion.cliente.like(cliente))

    if start:
        query = query.filter(Medicion.fecha >= start)
    if end:
        query = query.filter(Medicion.fecha <= end)

    # Paginación
    print(str(query))
    offset = (page - 1) * limit
    resultados = query.order_by(Medicion.fecha.asc()).offset(offset).limit(limit).all()
    
    print("→ Cliente recibido:", cliente)
    print("→ Resultados obtenidos:", resultados)
    # print("→ Cantidad:", len(resultados))

    # print("→ Primer resultado:", resultados[0].__dict__)

    if not resultados:
        raise HTTPException(status_code=404, detail="No se encontraron mediciones")


    output = [
        {
            "fecha": m.fecha,
            "presion": m.presion,
            "temperatura": m.temperatura,
            "volumen": m.volumen,
        }
        for m in resultados
    ]
    db.close()
    return output


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


@router.get("/anomalias/{cliente}")
def obtener_anomalias(
    cliente: str,
    start: datetime = Query(...),
    end: datetime = Query(...),
    db: Session = Depends(get_db)
):
    # 1. Cargar datos históricos para el cliente
    query = (
        db.query(Medicion)
        .filter(Medicion.cliente.ilike(cliente))
        .filter(Medicion.fecha >= start)
        .filter(Medicion.fecha <= end)
        .order_by(Medicion.fecha)
    )
    registros = query.all()

    if not registros:
        raise HTTPException(status_code=404, detail="No hay datos para el cliente en ese rango")

    df = pd.DataFrame([{
        "fecha": r.fecha,
        "Presion": r.presion,
        "Temperatura": r.temperatura,
        "Volumen": r.volumen
    } for r in registros])

    # 2. Cargar modelo correspondiente

    base_dir = Path(__file__).resolve().parent.parent
    modelo_path = base_dir / "models" / f"{cliente}_pipeline.pkl"
    if not modelo_path.exists():
        raise HTTPException(status_code=404, detail=f"No se encontró el modelo para {cliente}")

    modelo = joblib.load(modelo_path)

    
    # Preprocesar datos
    df = create_diff_variables(df)
    # df = df.dropna()
    # 3. Aplicar el modelo
    X = df[['Presion', 'Temperatura', 'Volumen','delta_volumen','delta_presion','delta_temperatura']]
    predicciones = modelo.predict_severity(X) 

    df["criticidad"] = predicciones

    # 4. Filtrar anomalías y formatear
    anomalias = df[df["criticidad"] != "normal"]
    print("🔍 Cantidad de anomalías:", len(anomalias))
    # print(anomalias.head().to_dict())
    print(anomalias.isna().sum())
    resultado = []
    for i, row in anomalias.iterrows():
        for var in ["Presion", "Temperatura", "Volumen"]:
            resultado.append({
                "fecha": row["fecha"],
                "variable": var,
                "valor": row[var],
                "criticidad": row["criticidad"]
            })
    print(resultado)
    return resultado    
