import os
import requests
from functools import wraps

from flask import (
    Flask,
    redirect,
    session,
    url_for,
    render_template,
    jsonify,
    request,
)

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from sqlalchemy import func

from models import (
    db,
    User,
    Role,
    HistorialConsulta,
    seed_roles,
    ROLE_HIERARCHY,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///climapp.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    seed_roles(app)

oauth = OAuth(app)

auth0 = oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)

AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")


def get_user():
    return session.get("user")


def get_roles():
    return session.get("roles", [])


def has_role(min_role):
    roles = get_roles()

    if not roles:
        return False

    user_level = max(
        ROLE_HIERARCHY.get(r, 0)
        for r in roles
    )

    return user_level >= ROLE_HIERARCHY.get(min_role, 0)


@app.context_processor
def inject_user_context():
    return {
        "user": get_user(),
        "roles": get_roles(),
        "has_role": has_role,
    }


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not get_user():
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated


def role_required(min_role):

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            if not has_role(min_role):
                return render_template("no_access.html"), 403

            return f(*args, **kwargs)

        return decorated

    return decorator


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/login")
def login():
    return auth0.authorize_redirect(
        redirect_uri=os.getenv("AUTH0_CALLBACK_URL"),
        prompt="login",
    )


@app.route("/callback")
def callback():

    token = auth0.authorize_access_token()
    userinfo = token.get("userinfo", {})

    auth0_id = userinfo.get("sub", "")

    if not auth0_id:
        return redirect(url_for("login"))

    db_user = User.query.filter_by(auth0_id=auth0_id).first()

    if not db_user:

        has_admin = User.query.filter_by(
            role_id=Role.query.filter_by(name="admin").first().id
        ).first()

        auto_role = (
            Role.query.filter_by(name="admin").first()
            if not has_admin
            else Role.query.filter_by(name="viewer").first()
        )

        db_user = User(
            auth0_id=auth0_id,
            email=userinfo.get("email", ""),
            name=userinfo.get("name", ""),
            picture=userinfo.get("picture", ""),
            role_id=auto_role.id,
        )

        db.session.add(db_user)
        db.session.commit()

    else:

        db_user.email = userinfo.get("email", db_user.email)
        db_user.name = userinfo.get("name", db_user.name)
        db_user.picture = userinfo.get("picture", db_user.picture)

        admin_role = Role.query.filter_by(name="admin").first()

        has_admin = User.query.filter(
            User.role_id == admin_role.id,
            User.id != db_user.id,
        ).first()

        if not has_admin and db_user.role_id != admin_role.id:
            db_user.role_id = admin_role.id

        db.session.commit()

    session["user"] = userinfo
    session["roles"] = [db_user.role.name] if db_user.role else []
    session["db_user_id"] = db_user.id

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/dashboard/clima")
@login_required
def clima():
    return render_template("sections/clima.html")


@app.route("/dashboard/clima/pronostico")
@login_required
def pronostico():
    return render_template("sections/pronostico.html")


@app.route("/dashboard/clima/historial")
@login_required
def historial():
    return render_template("sections/historial.html")


@app.route("/dashboard/clima/alertas")
@login_required
def alertas():
    return render_template("sections/alertas.html")

@app.route("/dashboard/usuarios")
@login_required
@role_required("admin")
def usuarios():

    all_users = User.query.all()
    all_roles = Role.query.all()

    return render_template(
        "sections/usuarios.html",
        all_users=all_users,
        all_roles=all_roles
    )


@app.route("/dashboard/config")
@login_required
def config():
    return render_template("sections/config.html")


# ==========================================================
# API DE ROLES
# ==========================================================

@app.route("/api/user/roles")
@login_required
def api_user_roles():
    return jsonify({
        "roles": get_roles()
    })


@app.route("/api/users", methods=["GET"])
@login_required
@role_required("admin")
def api_list_users():

    users = User.query.all()

    return jsonify([
        {
            "id": u.id,
            "auth0_id": u.auth0_id,
            "email": u.email,
            "name": u.name,
            "role": u.role.name if u.role else "viewer",
            "role_id": u.role_id,
            "created_at": (
                u.created_at.isoformat()
                if u.created_at
                else None
            ),
        }
        for u in users
    ])


@app.route("/api/users/<int:user_id>/role", methods=["PUT"])
@login_required
@role_required("admin")
def api_update_user_role(user_id):

    data = request.get_json()

    role_id = data.get("role_id")

    if not role_id:
        return jsonify({
            "error": "role_id requerido"
        }), 400

    role = Role.query.get(role_id)

    if not role:
        return jsonify({
            "error": "Rol no encontrado"
        }), 404

    target_user = User.query.get(user_id)

    if not target_user:
        return jsonify({
            "error": "Usuario no encontrado"
        }), 404

    target_user.role_id = role_id

    db.session.commit()

    if session.get("db_user_id") == user_id:
        session["roles"] = [role.name]

    return jsonify({
        "ok": True,
        "user_id": user_id,
        "role": role.name
    })


@app.route("/api/roles", methods=["GET"])
@login_required
def api_list_roles():

    roles = Role.query.all()

    return jsonify([
        {
            "id": r.id,
            "name": r.name,
            "level": r.level,
            "description": r.description
        }
        for r in roles
    ])


# ==========================================================
# API DEL CLIMA (Open-Meteo)
# ==========================================================

@app.route("/api/clima")
@login_required
def api_clima():

    ciudad = request.args.get("ciudad", "").strip()

    if ciudad == "":
        return jsonify({
            "error": "Debe indicar una ciudad."
        }), 400

    try:

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={ciudad}"
            "&count=10"
            "&language=es"
            "&format=json"
        )

        geo_response = requests.get(
            geo_url,
            timeout=10
        )

        geo_data = geo_response.json()

        if "results" not in geo_data:
            return jsonify({
                "error": "Ciudad no encontrada."
            }), 404

        lugar = geo_data["results"][0]

        if ciudad.lower() in ["san jose", "san josé"]:

            for resultado in geo_data["results"]:

                if resultado.get("country", "").lower() == "costa rica":
                    lugar = resultado
                    break

        latitud = lugar["latitude"]
        longitud = lugar["longitude"]

        clima_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={latitud}"
            f"&longitude={longitud}"
            "&current="
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "wind_speed_10m"
        )

        clima_response = requests.get(
            clima_url,
            timeout=10
        )

        clima_data = clima_response.json()

        actual = clima_data["current"]

        usuario_id = session.get("db_user_id")

        if usuario_id:

            consulta = HistorialConsulta(
                user_id=usuario_id,
                ciudad=lugar["name"],
                pais=lugar.get("country", ""),
                temperatura=actual["temperature_2m"],
                humedad=actual["relative_humidity_2m"],
                viento=actual["wind_speed_10m"],
                lluvia=actual["precipitation"],
                tipo_consulta="Clima"
            )

            db.session.add(consulta)
            db.session.commit()

        return jsonify({
            "ciudad": lugar["name"],
            "pais": lugar.get("country", ""),
            "latitud": latitud,
            "longitud": longitud,
            "temperatura": actual["temperature_2m"],
            "humedad": actual["relative_humidity_2m"],
            "sensacion": actual["apparent_temperature"],
            "lluvia": actual["precipitation"],
            "viento": actual["wind_speed_10m"]
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

    # ==========================================================
# API DEL PRONÓSTICO (7 DÍAS)
# ==========================================================

@app.route("/api/pronostico")
@login_required
def api_pronostico():

    ciudad = request.args.get("ciudad", "").strip()

    if ciudad == "":
        return jsonify({
            "error": "Debe indicar una ciudad."
        }), 400

    try:

        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={ciudad}"
            "&count=10"
            "&language=es"
            "&format=json"
        )

        geo = requests.get(
            geo_url,
            timeout=10
        ).json()

        if "results" not in geo:
            return jsonify({
                "error": "Ciudad no encontrada."
            }), 404

        lugar = geo["results"][0]

        if ciudad.lower() in ["san jose", "san josé"]:

            for resultado in geo["results"]:

                if resultado.get("country", "").lower() == "costa rica":
                    lugar = resultado
                    break

        lat = lugar["latitude"]
        lon = lugar["longitude"]

        forecast_url = (
            "https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}"
            f"&longitude={lon}"
            "&daily="
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min"
            "&timezone=auto"
        )

        forecast = requests.get(
            forecast_url,
            timeout=10
        ).json()

        dias = []

        for i in range(len(forecast["daily"]["time"])):

            dias.append({
                "fecha": forecast["daily"]["time"][i],
                "max": forecast["daily"]["temperature_2m_max"][i],
                "min": forecast["daily"]["temperature_2m_min"][i],
                "codigo": forecast["daily"]["weather_code"][i]
            })

        return jsonify({
            "ciudad": lugar["name"],
            "pais": lugar.get("country", ""),
            "dias": dias
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


# ==========================================================
# API DASHBOARD
# ==========================================================

@app.route("/api/dashboard")
@login_required
def api_dashboard():

    total = HistorialConsulta.query.count()

    temp_promedio = db.session.query(
        func.avg(HistorialConsulta.temperatura)
    ).scalar() or 0

    humedad_promedio = db.session.query(
        func.avg(HistorialConsulta.humedad)
    ).scalar() or 0

    viento_promedio = db.session.query(
        func.avg(HistorialConsulta.viento)
    ).scalar() or 0

    lluvia_promedio = db.session.query(
        func.avg(HistorialConsulta.lluvia)
    ).scalar() or 0

    ciudad = (
        db.session.query(
            HistorialConsulta.ciudad,
            func.count(HistorialConsulta.id)
        )
        .group_by(HistorialConsulta.ciudad)
        .order_by(func.count(HistorialConsulta.id).desc())
        .first()
    )

    ciudad_frecuente = ciudad[0] if ciudad else "Sin datos"

    total_ciudades = (
        db.session.query(
            HistorialConsulta.ciudad
        )
        .distinct()
        .count()
    )

    ciudades = (
        db.session.query(
            HistorialConsulta.ciudad,
            func.count(HistorialConsulta.id).label("cantidad")
        )
        .group_by(HistorialConsulta.ciudad)
        .order_by(func.count(HistorialConsulta.id).desc())
        .limit(5)
        .all()
    )

    consultas_por_ciudad = [
        {
            "ciudad": c.ciudad,
            "cantidad": c.cantidad
        }
        for c in ciudades
    ]

    return jsonify({

        "consultas": total,

        "temperatura_promedio": round(temp_promedio, 1),
        "humedad_promedio": round(humedad_promedio, 1),
        "viento_promedio": round(viento_promedio, 1),
        "lluvia_promedio": round(lluvia_promedio, 1),

        "ciudad_frecuente": ciudad_frecuente,
        "total_ciudades": total_ciudades,

        "consultas_por_ciudad": consultas_por_ciudad

    })

# ==========================================================
# API DE REPORTES
# ==========================================================

from datetime import datetime


@app.route("/api/reportes")
@login_required
def api_reportes():

    total = HistorialConsulta.query.count()

    temp_promedio = db.session.query(
        func.avg(HistorialConsulta.temperatura)
    ).scalar() or 0

    viento_promedio = db.session.query(
        func.avg(HistorialConsulta.viento)
    ).scalar() or 0

    ciudad = (
        db.session.query(
            HistorialConsulta.ciudad,
            func.count(HistorialConsulta.id)
        )
        .group_by(HistorialConsulta.ciudad)
        .order_by(func.count(HistorialConsulta.id).desc())
        .first()
    )

    ciudad_frecuente = ciudad[0] if ciudad else "Sin datos"

    if temp_promedio >= 35:
        riesgo = "🔴 Alto"
        conclusion = (
            "Se detectan temperaturas elevadas que podrían representar un riesgo ambiental."
        )

    elif temp_promedio >= 28:
        riesgo = "🟡 Moderado"
        conclusion = (
            "Las condiciones ambientales requieren monitoreo."
        )

    else:
        riesgo = "🟢 Bajo"
        conclusion = (
            "Las condiciones ambientales registradas son estables."
        )

    return jsonify({
        "fecha": datetime.now().strftime("%d/%m/%Y"),
        "consultas": total,
        "ciudad": ciudad_frecuente,
        "temperatura": round(temp_promedio, 1),
        "viento": round(viento_promedio, 1),
        "riesgo": riesgo,
        "conclusion": conclusion
    })


# ==========================================================
# API DEL HISTORIAL
# ==========================================================

@app.route("/api/historial")
@login_required
def api_historial():

    usuario_id = session.get("db_user_id")

    historial = (
        HistorialConsulta.query
        .filter_by(user_id=usuario_id)
        .order_by(HistorialConsulta.fecha_consulta.desc())
        .all()
    )

    datos = []

    for h in historial:

        if h.tipo_consulta.lower() == "clima":
            accion = "Consultó el clima"

        elif h.tipo_consulta.lower() in ["pronóstico", "pronostico"]:
            accion = "Consultó el pronóstico"

        else:
            accion = h.tipo_consulta

        datos.append({
            "fecha": h.fecha_consulta.strftime("%d/%m/%Y %H:%M"),
            "usuario": h.usuario.name if h.usuario.name else h.usuario.email,
            "accion": accion,
            "ciudad": h.ciudad,
            "pais": h.pais,
            "tipo": h.tipo_consulta
        })

    return jsonify(datos)


# ==========================================================
# API DE ALERTAS
# ==========================================================

@app.route("/api/alertas")
@login_required
def api_alertas():

    usuario_id = session.get("db_user_id")

    consulta = (
        HistorialConsulta.query
        .filter_by(user_id=usuario_id)
        .order_by(HistorialConsulta.fecha_consulta.desc())
        .first()
    )

    if not consulta:
        return jsonify({
            "error": "Primero debe realizar una consulta del clima."
        })

    alertas = []

    if consulta.temperatura >= 35:
        alertas.append({
            "nivel": "🔴 Alta",
            "titulo": "Calor extremo",
            "descripcion": "La temperatura supera los 35°C."
        })

    if consulta.viento >= 60:
        alertas.append({
            "nivel": "🟠 Media",
            "titulo": "Vientos fuertes",
            "descripcion": "Se detectan vientos fuertes."
        })

    if consulta.lluvia >= 50:
        alertas.append({
            "nivel": "🔵 Media",
            "titulo": "Lluvias intensas",
            "descripcion": "Existe riesgo de lluvias intensas."
        })

    if not alertas:
        alertas.append({
            "nivel": "🟢 Baja",
            "titulo": "Sin alertas",
            "descripcion": "No se detectan riesgos ambientales."
        })

    return jsonify({
        "ciudad": consulta.ciudad,
        "alertas": alertas
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(
        host="localhost",
        port=9900,
        debug=True
    )
    