// ==========================================================
// HISTORIAL DE CONSULTAS
// Obtiene y muestra el historial de consultas del usuario
// ==========================================================

async function cargarHistorial() {

    try {

        // Solicitar el historial al backend
        const respuesta = await fetch("/api/historial");

        // Convertir la respuesta a formato JSON
        const datos = await respuesta.json();

        // Obtener el cuerpo de la tabla donde se mostrará el historial
        const tbody = document.querySelector("#tablaHistorial tbody");

        // Limpiar la tabla antes de agregar los nuevos registros
        tbody.innerHTML = "";

        // Recorrer todas las consultas recibidas
        datos.forEach(h => {

            // Agregar cada consulta como una nueva fila de la tabla
            tbody.innerHTML += `
                <tr>
                    <td>${h.fecha}</td>
                    <td>${h.usuario}</td>
                    <td>${h.accion}</td>
                    <td>${h.ciudad}</td>
                    <td>${h.pais}</td>
                    <td>${h.tipo}</td>
                </tr>
            `;

        });

    }
    catch (error) {

        // Mostrar el error en la consola si ocurre algún problema
        console.error(error);

    }

}

// Cargar el historial automáticamente al abrir la página
window.onload = cargarHistorial;