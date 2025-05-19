FROM python:3.9.4-slim

# Instala git y otras dependencias básicas
RUN apt-get update && apt-get install -y build-essential python3-dev libpq-dev git
# Clona el repositorio directamente dentro del contenedor
RUN git clone https://github.com/paulguz261/MIAD_2025_proy_final.git /app

WORKDIR /app
RUN git checkout feature/ajuste-despliegue-productivo

RUN ls -la

RUN pip install --upgrade pip
# Instala las dependencias
RUN pip install --no-cache-dir -r requirements-2.txt --verbose

# Expone el puerto
EXPOSE 8000

# Comando para ejecutar la app (ajusta según tu estructura)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "backend.api.endpoints:app"]