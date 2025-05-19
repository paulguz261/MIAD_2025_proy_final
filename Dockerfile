FROM python:3.11-slim

# Instala git y otras dependencias básicas
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clona el repositorio directamente dentro del contenedor
RUN git clone https://github.com/paulguz261/MIAD_2025_proy_final.git /app

# Establece el directorio de trabajo
WORKDIR /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements-2.txt

# Expone el puerto
EXPOSE 8000

# Comando para ejecutar la app (ajusta según tu estructura)
CMD ["uvicorn", "backend.api.endpoints:app", "--host", "0.0.0.0", "--port", "8000"]