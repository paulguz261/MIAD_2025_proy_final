FROM python:3.9.4-slim

# Instala git y otras dependencias básicas
RUN apt-get update && apt-get install -y build-essential python3-dev libpq-dev >
# Clona el repositorio directamente dentro del contenedor
RUN git clone https://github.com/paulguz261/MIAD_2025_proy_final.git /app

WORKDIR /app
RUN git checkout main

RUN ls -la

RUN pip install --upgrade pip
# Instala las dependencias
RUN pip install --no-cache-dir -r requirements-2.txt --verbose

# Expone el puerto
EXPOSE 5000


# Comando para ejecutar la app (ajusta según tu estructura)
CMD ["python", "./backend/api/endpoints.py"]