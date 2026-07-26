async function cargarHistorial() {

    try {

        const respuesta = await fetch("/api/historial");

        const datos = await respuesta.json();

        const tbody = document.querySelector("#tablaHistorial tbody");

        tbody.innerHTML = "";

        datos.forEach(h => {

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

        console.error(error);

    }

}

window.onload = cargarHistorial;