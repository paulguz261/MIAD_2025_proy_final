import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def load_data(file_path):
    """
    Carga datos desde un archivo CSV.
    
    Args:
        file_path: Ruta al archivo CSV
        
    Returns:
        DataFrame con los datos cargados
    """
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error al cargar datos: {e}")
        return None

def preprocess_data(df):
    """
    Preprocesa los datos para análisis.
    
    Args:
        df: DataFrame con datos crudos
        
    Returns:
        DataFrame preprocesado
    """
    if df is None or df.empty:
        return None
    
    # Copiar DataFrame para no modificar el original
    processed_df = df.copy()
    
    # Convertir columna de fecha/hora a datetime
    if 'timestamp' in processed_df.columns:
        processed_df['timestamp'] = pd.to_datetime(processed_df['timestamp'])
    
    # Ordenar por fecha/hora
    if 'timestamp' in processed_df.columns:
        processed_df = processed_df.sort_values('timestamp')
    
    # Eliminar filas con valores faltantes
    processed_df = processed_df.dropna()
    
    # Eliminar duplicados
    processed_df = processed_df.drop_duplicates()
    
    # Agregar columnas derivadas
    if all(col in processed_df.columns for col in ['presion', 'temperatura', 'volumen']):
        # Calcular estadísticas básicas
        processed_df['presion_media'] = processed_df['presion'].rolling(window=6).mean()
        processed_df['temperatura_media'] = processed_df['temperatura'].rolling(window=6).mean()
        processed_df['volumen_media'] = processed_df['volumen'].rolling(window=6).mean()
        
        # Calcular variaciones
        processed_df['presion_var'] = processed_df['presion'].pct_change() * 100
        processed_df['temperatura_var'] = processed_df['temperatura'].pct_change() * 100
        processed_df['volumen_var'] = processed_df['volumen'].pct_change() * 100
    
    return processed_df

def extract_features(df):
    """
    Extrae características para el modelo de detección de anomalías.
    
    Args:
        df: DataFrame preprocesado
        
    Returns:
        DataFrame con características extraídas
    """
    if df is None or df.empty:
        return None
    
    # Copiar DataFrame para no modificar el original
    features_df = df.copy()
    
    # Extraer características temporales
    if 'timestamp' in features_df.columns:
        features_df['hour'] = features_df['timestamp'].dt.hour
        features_df['day'] = features_df['timestamp'].dt.day
        features_df['month'] = features_df['timestamp'].dt.month
        features_df['day_of_week'] = features_df['timestamp'].dt.dayofweek
        features_df['is_weekend'] = features_df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    # Extraer características de las variables
    if all(col in features_df.columns for col in ['presion', 'temperatura', 'volumen']):
        # Estadísticas de ventana deslizante
        for col in ['presion', 'temperatura', 'volumen']:
            # Media móvil
            features_df[f'{col}_rolling_mean_3'] = features_df[col].rolling(window=3).mean()
            features_df[f'{col}_rolling_mean_6'] = features_df[col].rolling(window=6).mean()
            features_df[f'{col}_rolling_mean_12'] = features_df[col].rolling(window=12).mean()
            
            # Desviación estándar móvil
            features_df[f'{col}_rolling_std_3'] = features_df[col].rolling(window=3).std()
            features_df[f'{col}_rolling_std_6'] = features_df[col].rolling(window=6).std()
            
            # Valores máximos y mínimos móviles
            features_df[f'{col}_rolling_max_6'] = features_df[col].rolling(window=6).max()
            features_df[f'{col}_rolling_min_6'] = features_df[col].rolling(window=6).min()
            
            # Rangos móviles
            features_df[f'{col}_rolling_range_6'] = features_df[f'{col}_rolling_max_6'] - features_df[f'{col}_rolling_min_6']
    
    # Eliminar filas con valores faltantes
    features_df = features_df.dropna()
    
    return features_df

def prepare_data_for_api(df, client_id):
    """
    Prepara los datos para enviar a través de la API.
    
    Args:
        df: DataFrame con datos
        client_id: ID del cliente
        
    Returns:
        Diccionario con datos formateados para la API
    """
    if df is None or df.empty:
        return {
            'presion': [],
            'temperatura': [],
            'volumen': []
        }
    
    # Filtrar por cliente si existe la columna
    if 'client_id' in df.columns:
        df = df[df['client_id'] == client_id]
    
    # Preparar datos para cada variable
    result = {
        'presion': [],
        'temperatura': [],
        'volumen': []
    }
    
    # Convertir DataFrame a formato para la API
    for col in ['presion', 'temperatura', 'volumen']:
        if col in df.columns and 'timestamp' in df.columns:
            for _, row in df.iterrows():
                result[col].append({
                    'time': row['timestamp'].strftime('%H:%M'),
                    'value': round(row[col], 1)
                })
    
    return result

def generate_mock_data(client_limits, hours=24):
    """
    Genera datos simulados para pruebas.
    
    Args:
        client_limits: Límites del cliente
        hours: Número de horas de datos a generar
        
    Returns:
        DataFrame con datos simulados
    """
    now = datetime.now()
    data = []
    
    for i in range(hours):
        time = now - timedelta(hours=i)
        
        # Generar datos para presión
        presion_min = client_limits['presion']['min']
        presion_max = client_limits['presion']['max']
        presion = np.random.uniform(presion_min, presion_max)
        
        # Generar datos para temperatura
        temp_min = client_limits['temperatura']['min']
        temp_max = client_limits['temperatura']['max']
        temperatura = np.random.uniform(temp_min, temp_max)
        
        # Generar datos para volumen
        vol_min = client_limits['volumen']['min']
        vol_max = client_limits['volumen']['max']
        volumen = np.random.uniform(vol_min, vol_max)
        
        # Agregar datos
        data.append({
            'timestamp': time,
            'presion': round(presion, 1),
            'temperatura': round(temperatura, 1),
            'volumen': round(volumen, 1)
        })
    
    # Convertir a DataFrame
    df = pd.DataFrame(data)
    
    # Invertir para que los datos más recientes estén al final
    df = df.iloc[::-1].reset_index(drop=True)
    
    return df 