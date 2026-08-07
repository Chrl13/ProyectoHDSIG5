// ==========================================================
// PRONÓSTICO DEL CLIMA
// Consulta el pronóstico y muestra la información en pantalla
// ==========================================================


// Devuelve un ícono según el código meteorológico recibido
function iconoClima(codigo){

    if(codigo===0) return "☀️";
    if([1,2].includes(codigo)) return "🌤";
    if(codigo===3) return "☁️";
    if([45,48].includes(codigo)) return "🌫";
    if([51,53,55,61,63,65,80,81,82].includes(codigo)) return "🌧";
    if([71,73,75,77,85,86].includes(codigo)) return "❄️";
    if([95,96,99].includes(codigo)) return "⛈";

    // Ícono por defecto
    return "🌍";

}


async function buscarPronostico(){

    // Obtener la ciudad ingresada por el usuario
    const ciudad=document.getElementById("ciudadPronostico").value;

    // Panel donde se mostrará el resultado
    const panel=document.getElementById("resultadoPronostico");

    // Mostrar un mensaje mientras se consulta la API
    panel.innerHTML="Consultando...";

    try{

        // Enviar la solicitud al backend
        const r=await fetch(
            "/api/pronostico?ciudad="+encodeURIComponent(ciudad)
        );

        // Convertir la respuesta a formato JSON
        const datos=await r.json();

        // Verificar si la API devolvió algún error
        if(datos.error){

            panel.innerHTML="<p>"+datos.error+"</p>";

            return;

        }

        // Crear el encabezado con la ciudad y el país
        let html=`<h3>${datos.ciudad}, ${datos.pais}</h3>`;

        html+=`<div class="cards">`;

        // Recorrer todos los días del pronóstico
        datos.dias.forEach(d=>{

            const fecha=new Date(d.fecha);

            // Crear una tarjeta para cada día
            html+=`

            <div class="card">

                <h3>${iconoClima(d.codigo)}</h3>

                <strong>${fecha.toLocaleDateString("es-ES",{
                    weekday:"long"
                })}</strong>

                <p>${d.fecha}</p>

                <hr>

                <p>🔺 Máx: ${d.max}°C</p>

                <p>🔻 Mín: ${d.min}°C</p>

            </div>

            `;

        });

        html+="</div>";

        // Mostrar el resultado en pantalla
        panel.innerHTML=html;

    }

    catch(e){

        // Mostrar un mensaje si ocurre algún error
        panel.innerHTML="Error al obtener el pronóstico.";

        console.log(e);

    }

}

// Ejecutar la consulta cuando se carga la página
buscarPronostico();