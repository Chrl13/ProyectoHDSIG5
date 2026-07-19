async function cargarHistorial() {

    const respuesta = await fetch("/api/historial");

    const datos = await respuesta.json();

    const tbody = document.querySelector("#tablaHistorial tbody");

    tbody.innerHTML = "";

    datos.forEach(h => {

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

cargarHistorial();