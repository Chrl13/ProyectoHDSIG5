// ==========================================================
// HISTORIAL DE CONSULTAS
// Obtiene y muestra el historial de consultas del usuario
// ==========================================================

async function cargarHistorial() {

    // Solicitar el historial al backend
    const respuesta = await fetch("/api/historial");

    // Convertir la respuesta a formato JSON
    const datos = await respuesta.json();

    // Obtener el cuerpo de la tabla
    const tbody = document.querySelector("#tablaHistorial tbody");

    // Limpiar la tabla antes de cargar nuevos datos
    tbody.innerHTML = "";

    // Recorrer todas las consultas recibidas
    datos.forEach(h => {

        // Agregar cada consulta como una nueva fila
        tbody.innerHTML += `
            <tr>
                <td>${h.fecha}</td>
                <td>${h.ciudad}</td>
                <td>${h.pais}</td>
                <td>${h.temperatura} °C</td>
                <td>${h.humedad}%</td>
                <td>${h.viento} km/h</td>
                <td>${h.lluvia} mm</td>
                <td>${h.tipo}</td>
            </tr>
        `;

    });

}

// Cargar el historial cuando se abre la página
cargarHistorial();