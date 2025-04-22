import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import io
import base64

def set_style():
    """
    Configura el estilo de las visualizaciones.
    """
    # Configurar estilo
    plt.style.use('dark_background')
    
    # Configurar colores
    sns.set_palette("husl")
    
    # Configurar fuentes
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']
    
    # Configurar tamaño de fuente
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10

def plot_time_series(df, variable, title, limits=None, save_path=None):
    """
    Genera un gráfico de series temporales.
    
    Args:
        df: DataFrame con datos
        variable: Nombre de la variable a graficar
        title: Título del gráfico
        limits: Diccionario con límites (min, max)
        save_path: Ruta para guardar el gráfico
        
    Returns:
        Ruta del archivo guardado o None si no se guarda
    """
    if df is None or df.empty or variable not in df.columns:
        return None
    
    # Configurar estilo
    set_style()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Graficar serie temporal
    ax.plot(df.index, df[variable], linewidth=2, color='#4CAF50')
    
    # Agregar límites si se proporcionan
    if limits:
        min_limit = limits.get('min')
        max_limit = limits.get('max')
        
        if min_limit is not None:
            ax.axhline(y=min_limit, color='#F44336', linestyle='--', alpha=0.7, label=f'Límite inferior: {min_limit}')
        
        if max_limit is not None:
            ax.axhline(y=max_limit, color='#F44336', linestyle='--', alpha=0.7, label=f'Límite superior: {max_limit}')
    
    # Configurar título y etiquetas
    ax.set_title(title, pad=20)
    ax.set_xlabel('Tiempo')
    ax.set_ylabel(variable.capitalize())
    
    # Configurar leyenda
    if limits:
        ax.legend(loc='upper right')
    
    # Configurar grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Rotar etiquetas del eje x
    plt.xticks(rotation=45)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar gráfico si se proporciona una ruta
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    # Convertir a base64 para mostrar en la web
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def plot_anomalies(df, variable, anomalies, title, limits=None, save_path=None):
    """
    Genera un gráfico de series temporales con anomalías resaltadas.
    
    Args:
        df: DataFrame con datos
        variable: Nombre de la variable a graficar
        anomalies: DataFrame con anomalías
        title: Título del gráfico
        limits: Diccionario con límites (min, max)
        save_path: Ruta para guardar el gráfico
        
    Returns:
        Ruta del archivo guardado o None si no se guarda
    """
    if df is None or df.empty or variable not in df.columns:
        return None
    
    # Configurar estilo
    set_style()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Graficar serie temporal
    ax.plot(df.index, df[variable], linewidth=2, color='#4CAF50', label='Normal')
    
    # Resaltar anomalías
    if anomalies is not None and not anomalies.empty:
        anomaly_indices = anomalies[anomalies['variable'] == variable.capitalize()].index
        if len(anomaly_indices) > 0:
            ax.scatter(anomaly_indices, df.loc[anomaly_indices, variable], 
                      color='#F44336', s=100, label='Anomalía')
    
    # Agregar límites si se proporcionan
    if limits:
        min_limit = limits.get('min')
        max_limit = limits.get('max')
        
        if min_limit is not None:
            ax.axhline(y=min_limit, color='#F44336', linestyle='--', alpha=0.7, label=f'Límite inferior: {min_limit}')
        
        if max_limit is not None:
            ax.axhline(y=max_limit, color='#F44336', linestyle='--', alpha=0.7, label=f'Límite superior: {max_limit}')
    
    # Configurar título y etiquetas
    ax.set_title(title, pad=20)
    ax.set_xlabel('Tiempo')
    ax.set_ylabel(variable.capitalize())
    
    # Configurar leyenda
    ax.legend(loc='upper right')
    
    # Configurar grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Rotar etiquetas del eje x
    plt.xticks(rotation=45)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar gráfico si se proporciona una ruta
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    # Convertir a base64 para mostrar en la web
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def plot_correlation_matrix(df, variables, title, save_path=None):
    """
    Genera una matriz de correlación.
    
    Args:
        df: DataFrame con datos
        variables: Lista de variables a incluir
        title: Título del gráfico
        save_path: Ruta para guardar el gráfico
        
    Returns:
        Ruta del archivo guardado o None si no se guarda
    """
    if df is None or df.empty:
        return None
    
    # Filtrar variables que existen en el DataFrame
    variables = [var for var in variables if var in df.columns]
    
    if not variables:
        return None
    
    # Configurar estilo
    set_style()
    
    # Calcular matriz de correlación
    corr = df[variables].corr()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Graficar matriz de correlación
    sns.heatmap(corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1, ax=ax)
    
    # Configurar título
    ax.set_title(title, pad=20)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar gráfico si se proporciona una ruta
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    # Convertir a base64 para mostrar en la web
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8')

def plot_distribution(df, variable, title, limits=None, save_path=None):
    """
    Genera un gráfico de distribución.
    
    Args:
        df: DataFrame con datos
        variable: Nombre de la variable a graficar
        title: Título del gráfico
        limits: Diccionario con límites (min, max)
        save_path: Ruta para guardar el gráfico
        
    Returns:
        Ruta del archivo guardado o None si no se guarda
    """
    if df is None or df.empty or variable not in df.columns:
        return None
    
    # Configurar estilo
    set_style()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Graficar distribución
    sns.histplot(df[variable], kde=True, color='#4CAF50', ax=ax)
    
    # Agregar límites si se proporcionan
    if limits:
        min_limit = limits.get('min')
        max_limit = limits.get('max')
        
        if min_limit is not None:
            ax.axvline(x=min_limit, color='#F44336', linestyle='--', alpha=0.7, label=f'Límite inferior: {min_limit}')
        
        if max_limit is not None:
            ax.axvline(x=max_limit, color='#F44336', linestyle='--', alpha=0.7, label=f'Límite superior: {max_limit}')
    
    # Configurar título y etiquetas
    ax.set_title(title, pad=20)
    ax.set_xlabel(variable.capitalize())
    ax.set_ylabel('Frecuencia')
    
    # Configurar leyenda
    if limits:
        ax.legend(loc='upper right')
    
    # Configurar grid
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar gráfico si se proporciona una ruta
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        return save_path
    
    # Convertir a base64 para mostrar en la web
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close()
    
    return base64.b64encode(image_png).decode('utf-8') 