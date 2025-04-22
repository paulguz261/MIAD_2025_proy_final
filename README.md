# Proyecto Final - Análisis de Datos de Agua

## Descripción
Este proyecto implementa un sistema de monitoreo y análisis de datos de agua, incluyendo detección de anomalías en presión, temperatura y volumen.

## Estructura del Proyecto
```
proyecto_final/
│
├── frontend/                  # Componentes frontend
│   ├── css/                  # Hojas de estilo CSS
│   ├── js/                   # Archivos JavaScript
│   └── index.html            # Página principal del dashboard
│
├── backend/                   # Componentes backend
│   ├── data/                 # Almacenamiento de datos
│   │   ├── raw/              # Datos sin procesar
│   │   └── processed/        # Datos procesados
│   ├── models/               # Modelos de ciencia de datos
│   ├── utils/                # Funciones de utilidad
│   └── api/                  # Endpoints de API
│
├── notebooks/                 # Jupyter notebooks
├── tests/                    # Archivos de prueba
├── config/                   # Archivos de configuración
└── docs/                     # Documentación
```

## Instalación
1. Clonar el repositorio
2. Instalar dependencias: `pip install -r requirements.txt`
3. Configurar variables de entorno en `config/config.yaml`

## Uso
1. Iniciar el servidor backend: `python backend/api/app.py`
2. Abrir `frontend/index.html` en un navegador web

## Características
- Dashboard interactivo para visualización de datos
- Detección de anomalías en tiempo real
- Límites dinámicos basados en patrones temporales
- Visualización de datos históricos

## Tecnologías
- Frontend: HTML, CSS, JavaScript, Chart.js
- Backend: Python, Flask, Pandas, Scikit-learn
- Visualización: Chart.js, D3.js 