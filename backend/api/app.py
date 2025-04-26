##este file no


from flask import Flask, jsonify, request
from flask_cors import CORS
import yaml
import os
import json
from datetime import datetime, timedelta
import random

# Cargar configuración
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas las rutas

# Ruta para obtener datos de un cliente
@app.route('/api/data/<client_id>', methods=['GET'])
def get_client_data(client_id):
    # Verificar si el cliente existe
    if client_id not in config['clients']:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Obtener parámetros de la consulta
    hours = request.args.get('hours', default=24, type=int)
    
    # Generar datos simulados (esto se reemplazará con datos reales)
    data = generate_mock_data(client_id, hours)
    
    return jsonify(data)

# Ruta para obtener límites de un cliente
@app.route('/api/limits/<client_id>', methods=['GET'])
def get_client_limits(client_id):
    # Verificar si el cliente existe
    if client_id not in config['clients']:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Obtener límites del cliente
    client_limits = config['clients'][client_id]
    
    return jsonify(client_limits)

# Ruta para obtener anomalías de un cliente
@app.route('/api/anomalies/<client_id>', methods=['GET'])
def get_client_anomalies(client_id):
    # Verificar si el cliente existe
    if client_id not in config['clients']:
        return jsonify({'error': 'Cliente no encontrado'}), 404
    
    # Obtener parámetros de la consulta
    hours = request.args.get('hours', default=24, type=int)
    
    # Generar anomalías simuladas (esto se reemplazará con detección real)
    anomalies = generate_mock_anomalies(client_id, hours)
    
    return jsonify(anomalies)

# Función para generar datos simulados
def generate_mock_data(client_id, hours):
    client_limits = config['clients'][client_id]
    now = datetime.now()
    
    data = {
        'presion': [],
        'temperatura': [],
        'volumen': []
    }
    
    for i in range(hours):
        time = now - timedelta(hours=i)
        time_str = time.strftime('%H:%M')
        
        # Generar datos para presión
        presion_min = client_limits['presion']['min']
        presion_max = client_limits['presion']['max']
        presion = random.uniform(presion_min, presion_max)
        
        # Generar datos para temperatura
        temp_min = client_limits['temperatura']['min']
        temp_max = client_limits['temperatura']['max']
        temperatura = random.uniform(temp_min, temp_max)
        
        # Generar datos para volumen
        vol_min = client_limits['volumen']['min']
        vol_max = client_limits['volumen']['max']
        volumen = random.uniform(vol_min, vol_max)
        
        # Agregar datos
        data['presion'].append({'time': time_str, 'value': round(presion, 1)})
        data['temperatura'].append({'time': time_str, 'value': round(temperatura, 1)})
        data['volumen'].append({'time': time_str, 'value': round(volumen, 1)})
    
    # Invertir listas para que los datos más recientes estén al final
    data['presion'].reverse()
    data['temperatura'].reverse()
    data['volumen'].reverse()
    
    return data

# Función para generar anomalías simuladas
def generate_mock_anomalies(client_id, hours):
    client_limits = config['clients'][client_id]
    now = datetime.now()
    anomaly_probability = config['anomaly_detection']['probability']
    
    anomalies = []
    
    for i in range(hours):
        time = now - timedelta(hours=i)
        time_str = time.strftime('%H:%M')
        
        # Decidir si hay anomalía en presión
        if random.random() < anomaly_probability:
            presion_min = client_limits['presion']['min']
            presion_max = client_limits['presion']['max']
            
            if random.random() < 0.5:
                # Anomalía por debajo del límite
                value = presion_min - random.uniform(0.1, 0.5)
                tipo = 'Valor bajo'
            else:
                # Anomalía por encima del límite
                value = presion_max + random.uniform(0.1, 0.5)
                tipo = 'Valor alto'
            
            anomalies.append({
                'fecha': time_str,
                'variable': 'Presión',
                'tipo': tipo,
                'criticidad': 'Alta' if abs(value - (presion_min if tipo == 'Valor bajo' else presion_max)) > 0.3 else 'Media'
            })
        
        # Decidir si hay anomalía en temperatura
        if random.random() < anomaly_probability:
            temp_min = client_limits['temperatura']['min']
            temp_max = client_limits['temperatura']['max']
            
            if random.random() < 0.5:
                # Anomalía por debajo del límite
                value = temp_min - random.uniform(1, 3)
                tipo = 'Valor bajo'
            else:
                # Anomalía por encima del límite
                value = temp_max + random.uniform(1, 3)
                tipo = 'Valor alto'
            
            anomalies.append({
                'fecha': time_str,
                'variable': 'Temperatura',
                'tipo': tipo,
                'criticidad': 'Alta' if abs(value - (temp_min if tipo == 'Valor bajo' else temp_max)) > 3 else 'Media'
            })
        
        # Decidir si hay anomalía en volumen
        if random.random() < anomaly_probability:
            vol_min = client_limits['volumen']['min']
            vol_max = client_limits['volumen']['max']
            
            if random.random() < 0.5:
                # Anomalía por debajo del límite
                value = vol_min - random.uniform(10, 30)
                tipo = 'Valor bajo'
            else:
                # Anomalía por encima del límite
                value = vol_max + random.uniform(10, 30)
                tipo = 'Valor alto'
            
            anomalies.append({
                'fecha': time_str,
                'variable': 'Volumen',
                'tipo': tipo,
                'criticidad': 'Alta' if abs(value - (vol_min if tipo == 'Valor bajo' else vol_max)) > 50 else 'Media'
            })
    
    # Ordenar anomalías por fecha (más recientes primero)
    anomalies.sort(key=lambda x: x['fecha'], reverse=True)
    
    # Limitar a las 5 anomalías más recientes
    return anomalies[:5]

if __name__ == '__main__':
    app.run(
        host=config['server']['host'],
        port=config['server']['port'],
        debug=config['server']['debug']
    ) 