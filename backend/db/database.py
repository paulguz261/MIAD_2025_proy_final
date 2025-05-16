# db/database.py
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


# Ruta al archivo SQLite
DATABASE_URL = "sqlite:///./contugas.db"
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "contugas.db"))
DATABASE_URL = f"sqlite:///{db_path}"

# Crear el engine de conexión
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False},
                       echo=True)  # <- esto activa el logging de consultas SQL

# Crear clase base para los modelos
Base = declarative_base()

# Sesión para interactuar con la base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tabla de mediciones
class Medicion(Base):
    __tablename__ = "mediciones"

    id = Column(Integer, primary_key=True, index=True)
    cliente = Column(String, index=True)
    fecha = Column(DateTime, index=True)
    presion = Column(Float)
    temperatura = Column(Float)
    volumen = Column(Float)

# Crear las tablas si no existen
def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    print("📍 Base de datos:", os.path.abspath("contugas.db"))
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
