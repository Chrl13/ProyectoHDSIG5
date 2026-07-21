let mapa = null;

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

        // ===========================
        // Calcular nivel de riesgo
        // ===========================

        let riesgo = "Bajo";
        let color = "green";

        if (datos.lluvia >= 10 || datos.viento >= 40) {
            riesgo = "Alto";
            color = "red";
        } else if (datos.temperatura >= 30) {
            riesgo = "Medio";
            color = "orange";
        }

        // ===========================
        // Mostrar mapa
        // ===========================

        const mapaDiv = document.getElementById("mapa");
        mapaDiv.style.display = "block";

        if (!mapa) {

            mapa = L.map("mapa");

            L.tileLayer(
                "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                {
                    attribution: "&copy; OpenStreetMap"
                }
            ).addTo(mapa);

        }

        mapa.setView(
            [datos.latitud, datos.longitud],
            10
        );

        // Elimina todos los marcadores y círculos anteriores
        mapa.eachLayer(function(layer) {

            if (!(layer instanceof L.TileLayer)) {
                mapa.removeLayer(layer);
            }

        });

        // Agrega el nuevo marcador
        L.marker([datos.latitud, datos.longitud])
            .addTo(mapa)
            .bindPopup(
                `<b>${datos.ciudad}</b><br>
                ${datos.pais}<br>
                <strong>Riesgo: ${riesgo}</strong>`
            )
            .openPopup();

        // Agrega el círculo de riesgo
        L.circle(
            [datos.latitud, datos.longitud],
            {
                radius: 5000,
                color: color,
                fillColor: color,
                fillOpacity: 0.35
            }
        ).addTo(mapa);

        setTimeout(() => {
            mapa.invalidateSize();
        }, 100);

    } catch (e) {

        contenedor.innerHTML =
            "<p style='color:red'>No fue posible consultar el clima.</p>";

        console.error(e);

    }

}