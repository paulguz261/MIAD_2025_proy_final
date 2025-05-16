# main_api.py

from fastapi import FastAPI, Query, HTTPException
from api.endpoints import router as api_router
import uvicorn

from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
import pandas as pd
import joblib
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# import contugas_anomaly_project.preprocess as pre
# import contugas_anomaly_project.config as cnf
# import contugas_anomaly_project.model as mdl

app = FastAPI(title="Contugas Anomaly Detection API")

# Incluir endpoints
# Allow frontend (JavaScript) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict to your frontend later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")