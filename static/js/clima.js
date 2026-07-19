async function buscarClima() {

    const ciudad = document.getElementById("ciudad").value;

    if (ciudad.trim() === "") {
        alert("Escribe una ciudad.");
        return;
    }

    const contenedor = document.getElementById("resultado");

    contenedor.innerHTML = "<p>Cargando...</p>";

    try {

        const respuesta = await fetch(
            "/api/clima?ciudad=" + encodeURIComponent(ciudad)
        );

        const datos = await respuesta.json();

        if (datos.error) {
            contenedor.innerHTML =
                "<p style='color:red'>" + datos.error + "</p>";
            return;
        }

        contenedor.innerHTML = `
            <div class="cards">

                <div class="card">
                    <h3>📍 Ciudad</h3>
                    <p>${datos.ciudad}</p>
                    <small>${datos.pais}</small>
                </div>

                <div class="card">
                    <h3>🌡 Temperatura</h3>
                    <p>${datos.temperatura} °C</p>
                </div>

                <div class="card">
                    <h3>💧 Humedad</h3>
                    <p>${datos.humedad}%</p>
                </div>

                <div class="card">
                    <h3>🌬 Viento</h3>
                    <p>${datos.viento} km/h</p>
                </div>

                <div class="card">
                    <h3>🌧 Lluvia</h3>
                    <p>${datos.lluvia} mm</p>
                </div>

                <div class="card">
                    <h3>🤒 Sensación</h3>
                    <p>${datos.sensacion} °C</p>
                </div>

            </div>
        `;

    } catch (e) {

        contenedor.innerHTML =
            "<p style='color:red'>No fue posible consultar el clima.</p>";

        console.error(e);

    }

}