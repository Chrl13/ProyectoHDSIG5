function iconoClima(codigo){

    if(codigo===0) return "☀️";
    if([1,2].includes(codigo)) return "🌤";
    if(codigo===3) return "☁️";
    if([45,48].includes(codigo)) return "🌫";
    if([51,53,55,61,63,65,80,81,82].includes(codigo)) return "🌧";
    if([71,73,75,77,85,86].includes(codigo)) return "❄️";
    if([95,96,99].includes(codigo)) return "⛈";

    return "🌍";
}

async function buscarPronostico(){

    const ciudad=document.getElementById("ciudadPronostico").value;

    const panel=document.getElementById("resultadoPronostico");

    panel.innerHTML="Consultando...";

    try{

        const r=await fetch(
            "/api/pronostico?ciudad="+encodeURIComponent(ciudad)
        );

        const datos=await r.json();

        if(datos.error){

            panel.innerHTML="<p>"+datos.error+"</p>";

            return;

        }

        let html=`<h3>${datos.ciudad}, ${datos.pais}</h3>`;

        html+=`<div class="cards">`;

        datos.dias.forEach(d=>{

            const fecha=new Date(d.fecha);

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

        panel.innerHTML=html;

    }

    catch(e){

        panel.innerHTML="Error al obtener el pronóstico.";

        console.log(e);

    }

}

buscarPronostico();