document.addEventListener("DOMContentLoaded", () => {
  cargarClientes();  // o el nombre de tu inicializador
});

// Función para crear una línea de límite
function createLimitLine(value, label, color) {
    return {
        type: 'line',
        yMin: value,
        yMax: value,
        borderColor: color,
        borderWidth: 2,
        borderDash: [5, 5],
        label: {
            content: label,
            enabled: true,
            position: 'end'
        }
    };
}

// Función para crear una zona sombreada
function createShadedArea(minValue, maxValue, color) {
    return {
        type: 'box',
        yMin: minValue,
        yMax: maxValue,
        backgroundColor: color,
        borderWidth: 0,
        drawTime: 'beforeDatasetsDraw'
    };
}

// Configuración común para los gráficos
const commonOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#2e2e2e'
      }
    },
    annotation: {
      annotations: {}
    },
    zoom: {
      pan: {
        enabled: true,
        mode: 'x',
        onPanComplete: ({ chart }) => {
          if (chart === presionChart) sincronizarZoom(presionChart, [temperaturaChart, volumenChart]);
          if (chart === temperaturaChart) sincronizarZoom(temperaturaChart, [presionChart, volumenChart]);
          if (chart === volumenChart) sincronizarZoom(volumenChart, [presionChart, temperaturaChart]);
        }
      },
      zoom: {
        wheel: { enabled: true },
        pinch: { enabled: true },
        mode: 'x',
        onZoomComplete: ({ chart }) => {
          if (chart === presionChart) sincronizarZoom(presionChart, [temperaturaChart, volumenChart]);
          if (chart === temperaturaChart) sincronizarZoom(temperaturaChart, [presionChart, volumenChart]);
          if (chart === volumenChart) sincronizarZoom(volumenChart, [presionChart, temperaturaChart]);
        }
      }
    }
  },
  scales: {
    x: {
      border: {
        color: '#2e2e2e'
      },
      grid: {
        color: '#ccc'
      },
      ticks: {
        color: '#2e2e2e',
        maxRotation: 45,
        minRotation: 45,
        padding: 10
      }
    },
    y: {
      border: {
        color: '#2e2e2e'
      },
      grid: {
        color: '#ccc'
      },
      ticks: {
        color: '#2e2e2e',
        padding: 10
      },
      title: {
        display: true,
        color: '#2e2e2e',
        text: ''
      }
    }
  }
};


// Crear gráficos
const presionChart = new Chart(
    document.getElementById('graficoPresion'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Presión (bar)',
                data: [],
                borderColor: '#2db84d',
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Presión (bar)',
                        color: '#2e2e2e'
                    }
                }
            },
        }
    }
);

const temperaturaChart = new Chart(
    document.getElementById('graficoTemperatura'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Temperatura (°C)',
                data: [], 
                borderColor: '#2db84d',
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Temperatura (°C)',
                        color: '#2e2e2e'
                    }
                }
            },
        }
    }
);

const volumenChart = new Chart(
    document.getElementById('graficoVolumen'),
    {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Volumen (m³)',
                data: [], 
                borderColor: '#2db84d',
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    title: {
                        display: true,
                        text: 'Volumen (m³)',
                        color: '#2e2e2e'
                    }
                }
            },
        }
    }
);

// Función para obtener límites variables basados en la hora actual
function getVariableLimits(limits, time) {
    // Si hay una función getDynamicLimits, usarla
    if (limits.getDynamicLimits) {
        return limits.getDynamicLimits(time);
    }
    
    // Si hay límites variables predefinidos, usarlos
    if (limits.variableLimits) {
        const hour = time.getHours();
        const day = time.getDay();
        
        // Buscar el límite más cercano a la hora actual
        let closestLimit = limits.variableLimits[0];
        let minDiff = Infinity;
        
        for (const limit of limits.variableLimits) {
            if (limit.hour !== undefined) {
                // Límites por hora
                const diff = Math.abs(limit.hour - hour);
                if (diff < minDiff) {
                    minDiff = diff;
                    closestLimit = limit;
                }
            } else if (limit.day !== undefined) {
                // Límites por día
                if (limit.day === day) {
                    return { min: limit.min, max: limit.max };
                }
            }
        }
        
        return { min: closestLimit.min, max: closestLimit.max };
    }
    
    // Si no hay límites variables, usar los límites fijos
    return { min: limits.min, max: limits.max };
}

function obtenerCriticidadMaxima(lista) {
    if (lista.includes("alta")) return "alta";
    if (lista.includes("media")) return "media";
    if (lista.includes("leve")) return "leve";
    return "normal";
}


// Función para actualizar la tabla de anomalías
function actualizarTablaAnomalias(anomalias) {
    const tabla = document.getElementById("anomaliasTable");
    const tbody = tabla.querySelector("tbody");
    tbody.innerHTML = "";  // ✅ Limpia solo las filas


    // Agrupar anomalías por fecha
    const agrupadas = {};

    anomalias.forEach(a => {
        const fecha = new Date(a.fecha).toLocaleString();

        if (!agrupadas[fecha]) {
            agrupadas[fecha] = {
                fecha,
                presion: null,
                temperatura: null,
                volumen: null,
                criticidades: []
            };
        }

        const registro = agrupadas[fecha];

        if (a.variable.toLowerCase() === "presion") registro.presion = a.valor;
        if (a.variable.toLowerCase() === "temperatura") registro.temperatura = a.valor;
        if (a.variable.toLowerCase() === "volumen") registro.volumen = a.valor;

        registro.criticidades.push(a.criticidad);
    });

    // Convertir objeto a array y ordenar por fecha descendente
    const filas = Object.values(agrupadas).sort((a, b) => new Date(b.fecha) - new Date(a.fecha));

    // Renderizar filas
    filas.forEach(r => {
        const fila = document.createElement("tr");

        const tdFecha = document.createElement("td");
        tdFecha.textContent = r.fecha;

        const tdPresion = document.createElement("td");
        tdPresion.textContent = r.presion !== null ? r.presion.toFixed(2) : "-";

        const tdTemp = document.createElement("td");
        tdTemp.textContent = r.temperatura !== null ? r.temperatura.toFixed(2) : "-";

        const tdVol = document.createElement("td");
        tdVol.textContent = r.volumen !== null ? r.volumen.toFixed(2) : "-";

        const tdCrit = document.createElement("td");
        const nivel = obtenerCriticidadMaxima(r.criticidades);
        tdCrit.textContent = nivel;
        tdCrit.classList.add(`anomalia-${nivel}`);
        tdCrit.style.fontWeight = "bold";

        fila.append(tdFecha, tdPresion, tdTemp, tdVol, tdCrit);
        tbody.appendChild(fila);
    });

    if (filas.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");
        celda.colSpan = 5;
        celda.style.textAlign = "center";
        celda.textContent = "No se detectaron anomalías en el período seleccionado";
        fila.appendChild(celda);
        tbody.appendChild(fila);
    }
}


// Función para actualizar el dashboard
async function updateDashboard() {
    console.log("🔁 updateDashboard ejecutado");
    const cliente = document.getElementById('clientSelect').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    console.log("startDate:", startDate);
    console.log("endDate:", endDate);

    const params = new URLSearchParams();
    if (startDate) params.append("start", startDate);
    if (endDate) params.append("end", endDate);

    const url = `http://localhost:8000/api/mediciones/${cliente}?${params.toString()}`;
    const anomaliasUrl = `http://localhost:8000/api/anomalias/${cliente}?${params.toString()}`;

    try {
        const [response, resAnomalias] = await Promise.all([
            fetch(url),
            fetch(anomaliasUrl)
        ]);

        if (!resAnomalias.ok) {
            console.warn("❌ Error al obtener anomalías:", resAnomalias.status);
        }

        if (!response.ok) throw new Error("No se encontraron datos");
        const data = await response.json();

        // actualiza tabla de anomalias
        const anomalias = await resAnomalias.json();
        actualizarTablaAnomalias(anomalias);
        actualizarTarjetaEstado(data, anomalias);


        const labels = data.map(d => new Date(d.fecha).toLocaleString());
        const presionData = data.map(d => d.presion);
        const temperaturaData = data.map(d => d.temperatura);
        const volumenData = data.map(d => d.volumen);

        document.getElementById('presionActual').textContent = presionData.at(-1).toFixed(2);
        document.getElementById('temperaturaActual').textContent = temperaturaData.at(-1).toFixed(2);
        document.getElementById('volumenActual').textContent = volumenData.at(-1).toFixed(2);

        const expand = (arr, margen) => {
            const min = Math.min(...arr);
            const max = Math.max(...arr);
            return { min: Math.floor(min - margen), max: Math.ceil(max + margen) };
        };

        // -------- PRESIÓN --------
        presionChart.data.labels = labels;
        presionChart.data.datasets = [presionChart.data.datasets[0]];
        presionChart.data.datasets[0].data = presionData;
        const presionLimits = expand(presionData, 0.2);
        presionChart.options.scales.y.min = presionLimits.min;
        presionChart.options.scales.y.max = presionLimits.max;

        // -------- TEMPERATURA --------
        temperaturaChart.data.labels = labels;
        temperaturaChart.data.datasets = [temperaturaChart.data.datasets[0]];
        temperaturaChart.data.datasets[0].data = temperaturaData;
        const tempLimits = expand(temperaturaData, 1);
        temperaturaChart.options.scales.y.min = tempLimits.min;
        temperaturaChart.options.scales.y.max = tempLimits.max;

        // -------- VOLUMEN --------
        volumenChart.data.labels = labels;
        volumenChart.data.datasets = [volumenChart.data.datasets[0]];
        volumenChart.data.datasets[0].data = volumenData;
        const volLimits = expand(volumenData, 20);
        volumenChart.options.scales.y.min = volLimits.min;
        volumenChart.options.scales.y.max = volLimits.max;

        const niveles = [
            { nivel: "alta", color: "red" },
            { nivel: "media", color: "orange" },
            { nivel: "leve", color: "yellow" }
        ];

        for (const { nivel, color } of niveles) {
            presionChart.data.datasets.push(crearDatasetAnomalias(anomalias, "Presion", nivel, color));
            temperaturaChart.data.datasets.push(crearDatasetAnomalias(anomalias, "Temperatura", nivel, color));
            volumenChart.data.datasets.push(crearDatasetAnomalias(anomalias, "Volumen", nivel, color));
        }

        presionChart.update();
        temperaturaChart.update();
        volumenChart.update();

        console.log("📊 presionChart datasets:", presionChart.data.datasets);


    } catch (error) {
        alert("Error al cargar datos: " + error.message);
    }
}



async function establecerFechasPorDefecto(cliente) {
try {
    const response = await fetch(`http://localhost:8000/api/clientes/${cliente}/rango-fechas`);
    const rango = await response.json();

    console.log("rango:", rango);
    if (!rango.max_fecha) throw new Error("No hay datos disponibles");

    const maxFecha = new Date(rango.max_fecha);
    const minFecha = new Date(maxFecha);
    minFecha.setDate(maxFecha.getDate() - 30);
    console.log("minFecha:", minFecha.toISOString());
    console.log("minFecha.slice(0, 16):", minFecha.toISOString().slice(0, 16));
    console.log("maxFecha:", maxFecha.toISOString());
    console.log("minFecha.slice(0, 16):", maxFecha.toISOString().slice(0, 16));
    

    //document.getElementById("startDate").value = minFecha.toISOString().split("T")[0];
    document.getElementById("startDate").value = minFecha.toISOString().slice(0, 16);
    //document.getElementById("endDate").value = maxFecha.toISOString().split("T")[0];
    document.getElementById("endDate").value = maxFecha.toISOString().slice(0,16);

} catch (error) {
    console.warn("Error estableciendo fechas por defecto:", error.message);
    const hoy = new Date();
    const hace30 = new Date();
    hace30.setDate(hoy.getDate() - 30);

    document.getElementById("startDate").value = hace30.toISOString().split("T")[0];
    document.getElementById("endDate").value = hoy.toISOString().split("T")[0];
}
}


async function cargarClientes() {
    try {
        const response = await fetch("http://localhost:8000/api/clientes");
        const clientes = await response.json();

        const select = document.getElementById("clientSelect");
        select.innerHTML = ""; // limpiar opciones anteriores

        clientes.forEach(cliente => {
            const option = document.createElement("option");
            option.value = cliente;
            option.textContent = cliente;
            select.appendChild(option);
        });

    const clienteSeleccionado = clientes[0];
    document.getElementById("clientSelect").value = clienteSeleccionado;

    // Establecer fechas con base en el último dato real
    await establecerFechasPorDefecto(clienteSeleccionado);
    updateDashboard();

    // Agregar listeners
    document.getElementById("clientSelect").addEventListener("change", async () => {
        const nuevoCliente = document.getElementById("clientSelect").value;
        await establecerFechasPorDefecto(nuevoCliente);
        updateDashboard();
    });
    document.getElementById("startDate").addEventListener("change", updateDashboard);
    document.getElementById("endDate").addEventListener("change", updateDashboard);


    } catch (error) {
        console.error("Error al cargar clientes:", error);
    }
}

function crearDatasetAnomalias(anomalias, variable, nivel, color) {
    const datos = anomalias
        .filter(a => a.variable === variable && a.criticidad === nivel)
        .map(a => ({
            x: new Date(a.fecha).toLocaleString(),
            y: a.valor
        }));

    return {
        type: 'scatter',
        label: `Anomalías ${nivel}`,
        data: datos,
        parsing: false,
        pointBackgroundColor: color,
        pointRadius: 6,
        showLine: false
    };
}


function sincronizarZoom(chartOrigen, chartsDestino) {
    const range = chartOrigen.scales.x;

    chartsDestino.forEach(chart => {
        chart.options.scales.x.min = range.min;
        chart.options.scales.x.max = range.max;
        chart.update('none');
    });
}

function actualizarTarjetaEstado(data, anomalias) {
    const presionData = data.map(d => d.presion);
    const temperaturaData = data.map(d => d.temperatura);
    const volumenData = data.map(d => d.volumen);
    const labels = data.map(d => new Date(d.fecha).toLocaleString());

    // Calcular promedios
    const promedioPresion = (presionData.reduce((a, b) => a + b, 0) / presionData.length).toFixed(2);
    const promedioTemperatura = (temperaturaData.reduce((a, b) => a + b, 0) / temperaturaData.length).toFixed(2);
    const promedioVolumen = (volumenData.reduce((a, b) => a + b, 0) / volumenData.length).toFixed(2);


    // Mostrar promedios
    document.getElementById('promedioPresion').textContent = promedioPresion;
    document.getElementById('promedioTemperatura').textContent = promedioTemperatura;
    document.getElementById('promedioVolumen').textContent = promedioVolumen;

    // Últimos valores
    document.getElementById('presionActual').textContent = presionData.at(-1).toFixed(2);
    document.getElementById('temperaturaActual').textContent = temperaturaData.at(-1).toFixed(2);
    document.getElementById('volumenActual').textContent = volumenData.at(-1).toFixed(2);

    // Anomalías detectadas
    document.getElementById('cantidadAnomalias').textContent = (anomalias.length / 3).toFixed(0);

    // Estado del cliente (último punto)
    const ultimaFecha = labels.at(-1);
    const ultimaAnomalia = anomalias.find(a => new Date(a.fecha).toLocaleString() === ultimaFecha);

    const estado = document.getElementById('estadoCliente');
    if (ultimaAnomalia) {
        estado.textContent = "⚠️ Alerta";
        estado.className = "status-indicator status-warning";
    } else {
        estado.textContent = "✅ Normal";
        estado.className = "status-indicator status-normal";
    }
}

// Actualizar datos cada 5 segundos
setInterval(updateDashboard, 500000);



function sincronizarZoom(chartOrigen, chartsDestino) {
  const range = chartOrigen.scales.x;
  chartsDestino.forEach(chart => {
    chart.options.scales.x.min = range.min;
    chart.options.scales.x.max = range.max;
    chart.update('none');
  });
}

function resetZoomTodos() {
  presionChart.resetZoom();
  temperaturaChart.resetZoom();
  volumenChart.resetZoom();
}