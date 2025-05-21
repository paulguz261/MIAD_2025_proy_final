const host = window.location.origin;
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


// Función optimizada para actualizar la tabla de anomalías
function actualizarTablaAnomalias(anomalias) {
    const tabla = document.getElementById("anomaliasTable");
    const tbody = tabla.querySelector("tbody");
    tbody.innerHTML = "";  // Limpiar solo las filas de la tabla

    // Crear un fragmento de documento para reducir las manipulaciones del DOM
    const fragment = document.createDocumentFragment();

    if (anomalias.length === 0) {
        const fila = document.createElement("tr");
        const celda = document.createElement("td");
        celda.colSpan = 5;
        celda.style.textAlign = "center";
        celda.textContent = "No se detectaron anomalías en el período seleccionado";
        fila.appendChild(celda);
        fragment.appendChild(fila);
    } else {
        anomalias.forEach(r => {
            const fila = document.createElement("tr");

            const tdFecha = document.createElement("td");
            tdFecha.textContent = r.Fecha;

            const tdPresion = document.createElement("td");
            tdPresion.textContent = r.Presion !== null ? r.Presion.toFixed(2) : "-";

            const tdTemp = document.createElement("td");
            tdTemp.textContent = r.Temperatura !== null ? r.Temperatura.toFixed(2) : "-";

            const tdVol = document.createElement("td");
            tdVol.textContent = r.Volumen !== null ? r.Volumen.toFixed(2) : "-";

            const tdCrit = document.createElement("td");
            const nivel = obtenerCriticidadMaxima(r.criticidad);
            tdCrit.textContent = nivel;
            tdCrit.classList.add(`anomalia-${nivel}`, "font-bold");  // Agregar clase para el font-weight

            fila.append(tdFecha, tdPresion, tdTemp, tdVol, tdCrit);
            fragment.appendChild(fila);
        });
    }

    // Insertar todas las filas de una sola vez
    tbody.appendChild(fragment);
}


// Función para actualizar el dashboard
async function updateDashboard() {
    console.log("🔁 updateDashboard ejecutado");
    const cliente = document.getElementById('clientSelect').value;
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    console.log("startDate:", startDate);
    console.log("endDate:", endDate);
    console.log("cliente:", cliente)
    if(cliente !== ""){
        const params = new URLSearchParams();
    if (startDate) params.append("start", startDate);
    if (endDate) params.append("end", endDate);

    const anomaliasUrl = `${host}/api/anomalias/${cliente}?${params.toString()}`;

    try {
        const [resAnomalias] = await Promise.all([
            fetch(anomaliasUrl)
        ]);

        if (!resAnomalias.ok) {
            console.warn("❌ Error al obtener anomalías:", resAnomalias.status);
        }
        
        // actualiza tabla de anomalias
        const anomalias = await resAnomalias.json();
        
        const anomalias_all_data = anomalias.data

        const data_presion = anomalias.presion.data
        const chartset_point_presion = anomalias.presion.data_points

        const data_volumen = anomalias.volumen.data
        const chartset_point_volumen = anomalias.volumen.data_points

        const data_temperatura = anomalias.temperatura.data
        const chartset_point_temperatura = anomalias.temperatura.data_points

        self.onmessage = function (e) {
            const data = e.data; // por ejemplo, un array grande
            const result = procesarDatos(data); // aquí haces lo pesado
          
            self.postMessage(result); // devuelve resultado al hilo principal
          };
          
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                showDashboard(data_presion, data_temperatura, data_volumen,
                    chartset_point_presion, chartset_point_temperatura, chartset_point_volumen);
              console.log("✔️ Todas las funciones ejecutadas durante tiempo ocioso");
            });
          } else {
            setTimeout(() => {
                showDashboard(data_presion, data_temperatura, data_volumen,
                    chartset_point_presion, chartset_point_temperatura, chartset_point_volumen);
              console.log("✔️ Todas las funciones ejecutadas con fallback");
            }, 10);
          }
          actualizarTarjetaEstado(data_temperatura, data_volumen, data_presion,
            anomalias.temperatura.average, anomalias.presion.average, anomalias.volumen.average
          );
          actualizarTablaAnomalias(anomalias_all_data);
          


        


    } catch (error) {
        alert("Error al cargar datos: " + error.message);
    }
    }
    
}


async function loadChartTemperatura(data_temperatura, chartset_data){
    temperaturaChart.data.labels = data_temperatura.fecha;
    temperaturaChart.data.datasets = [temperaturaChart.data.datasets[0]];
    temperaturaChart.data.datasets[0].data = data_temperatura.valor ;
    const tempLimits = expand(data_temperatura.valor, 1);
    temperaturaChart.options.scales.y.min = tempLimits.min;
    temperaturaChart.options.scales.y.max = tempLimits.max;
    const niveles = [
        { nivel: "alta", color: "red" },
        { nivel: "media", color: "orange" },
        { nivel: "leve", color: "yellow" }
    ];

    for (const { nivel, color } of niveles) {
        temperaturaChart.data.datasets.push(crearDatasetAnomalias(chartset_data[nivel], nivel, color));
    }
    temperaturaChart.update();

}

async function loadChartVolumen(data_volumen, chartset_data){
    volumenChart.data.labels = data_volumen.fecha;
    volumenChart.data.datasets = [volumenChart.data.datasets[0]];
    volumenChart.data.datasets[0].data = data_volumen.valor;
    const volLimits = expand(data_volumen.valor, 20);
    volumenChart.options.scales.y.min = volLimits.min;
    volumenChart.options.scales.y.max = volLimits.max;
    const niveles = [
        { nivel: "alta", color: "red" },
        { nivel: "media", color: "orange" },
        { nivel: "leve", color: "yellow" }
    ];

    for (const { nivel, color } of niveles) {
        volumenChart.data.datasets.push(crearDatasetAnomalias(chartset_data[nivel], nivel, color));
    }
    volumenChart.update();
}



async function loadChartPresion(data_presion, chartset_data){
    presionChart.data.labels = data_presion.fecha;
    presionChart.data.datasets = [presionChart.data.datasets[0]];
    presionChart.data.datasets[0].data = data_presion.valor;
    const presionLimits = expand(data_presion.valor, 0.2);
    presionChart.options.scales.y.min = presionLimits.min;
    presionChart.options.scales.y.max = presionLimits.max;
    const niveles = [
        { nivel: "alta", color: "red" },
        { nivel: "media", color: "orange" },
        { nivel: "leve", color: "yellow" }
    ];

    for (const { nivel, color } of niveles) {
        presionChart.data.datasets.push(crearDatasetAnomalias(chartset_data[nivel], nivel, color));
    }
    presionChart.update();
}

const expand = (arr, margen) => {
    const min = Math.min(...arr);
    const max = Math.max(...arr);
    return { min: Math.floor(min - margen), max: Math.ceil(max + margen) };
};

async function showDashboard(data_presion, data_temperatura, data_volumen,
    chartset_point_presion, chartset_point_temperatura, chartset_point_volumen
){
    

    await loadChartTemperatura(data_temperatura, chartset_point_temperatura )
    await loadChartVolumen(data_volumen, chartset_point_volumen)
    await loadChartPresion(data_presion, chartset_point_presion)

    console.log("📊 presionChart datasets:", presionChart.data.datasets);
}

async function establecerFechasPorDefecto(cliente) {
    if(cliente !== undefined){
        try {
            const response = await fetch(`${host}/api/clientes/${cliente}/rango-fechas`);
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
}


async function cargarClientes() {
    try {
        const response = await fetch(`${host}/api/clientes`);
        const clientes = await response.json();

        const select = document.getElementById("clientSelect");
        select.innerHTML = ""; // limpiar opciones anteriores
        clientes.clientes.forEach(cliente => {
            const option = document.createElement("option");
            option.value = cliente;
            option.textContent = cliente;
            select.appendChild(option);
        });

    const clienteSeleccionado = clientes[0];
    document.getElementById("clientSelect").value = clienteSeleccionado;

    // Establecer fechas con base en el último dato real
    await establecerFechasPorDefecto(clienteSeleccionado);

    // Agregar listeners
    document.getElementById("clientSelect").addEventListener("change", async () => {
        const nuevoCliente = document.getElementById("clientSelect").value;
        await establecerFechasPorDefecto(nuevoCliente);
    });
    document.getElementById("btnFilter").addEventListener("click", updateDashboard);


    } catch (error) {
        console.error("Error al cargar clientes:", error);
    }
}

function crearDatasetAnomalias(data_points,nivel, color) {
    return {
        type: 'scatter',
        label: `Anomalías ${nivel}`,
        data: data_points,
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

function actualizarTarjetaEstado(data_temperatura, data_volumen, data_presion,
    prom_temperatura, prom_presion, prom_volumen
) {
    
    // Mostrar promedios
    document.getElementById('promedioPresion').textContent = prom_presion;
    document.getElementById('promedioTemperatura').textContent = prom_temperatura;
    document.getElementById('promedioVolumen').textContent = prom_volumen;
    // Últimos valores
    console.log("data presion")
    console.log(data_presion.average)
    document.getElementById('presionActual').textContent = Number(data_presion.valor.at(-1)).toFixed(2);
    document.getElementById('temperaturaActual').textContent = Number(data_temperatura.valor.at(-1)).toFixed(2);
    document.getElementById('volumenActual').textContent = Number(data_volumen.valor.at(-1)).toFixed(2);

    // Anomalías detectadas
    document.getElementById('cantidadAnomalias').textContent = Number((data_presion.valor.length + data_temperatura.valor.length 
        + data_volumen.valor.length / 3)).toFixed(0);

    const estado = document.getElementById('estadoCliente');
    if (data_temperatura.criticidad.at(-1) !== 'normal' ||
    data_presion.criticidad.at(-1) !== 'normal'||
    data_volumen.criticidad.at(-1) !== 'normal') {
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


window.addEventListener("load", () => {
    const tiempo = performance.now();
    console.log(`Tiempo total hasta onload: ${tiempo.toFixed(2)} ms`);
});