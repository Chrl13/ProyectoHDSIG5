import os
import json
import base64
import requests
from functools import wraps
from flask import Flask, redirect, session, url_for, render_template, jsonify
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

oauth = OAuth(app)
auth0 = oauth.register(
    "auth0",
    client_id=os.getenv("AUTH0_CLIENT_ID"),
    client_secret=os.getenv("AUTH0_CLIENT_SECRET"),
    server_metadata_url=f"https://{os.getenv('AUTH0_DOMAIN')}/.well-known/openid-configuration",
    client_kwargs={"scope": "openid profile email"},
)

ROLE_HIERARCHY = {"admin": 3, "operator": 2, "viewer": 1}
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
MANAGEMENT_API = f"https://{AUTH0_DOMAIN}/api/v2"
ROLES_CLAIM = f"https://{AUTH0_DOMAIN}/roles"


def get_management_token():
    resp = requests.post(
        f"https://{AUTH0_DOMAIN}/oauth/token",
        json={
            "client_id": AUTH0_CLIENT_ID,
            "client_secret": AUTH0_CLIENT_SECRET,
            "audience": MANAGEMENT_API,
            "grant_type": "client_credentials",
        },
        timeout=10,
    )
    data = resp.json()
    app.logger.info(f"Management token response: status={resp.status_code} keys={list(data.keys())}")
    if "access_token" not in data:
        app.logger.error(f"Management token error: {data}")
        return None, data
    return data["access_token"], None


def get_user_roles(user_id):
    token, error = get_management_token()
    if not token:
        return [], error
    resp = requests.get(
        f"{MANAGEMENT_API}/users/{user_id}/roles",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    data = resp.json()
    app.logger.info(f"Roles response: status={resp.status_code} data={data}")
    if resp.status_code != 200:
        return [], data
    return [r.get("name", "") for r in data.get("roles", [])], None


def get_user():
    return session.get("user")


def get_roles():
    return session.get("roles", [])


def has_role(min_role):
    roles = get_roles()
    if not roles:
        return False
    user_level = max(ROLE_HIERARCHY.get(r, 0) for r in roles)
    return user_level >= ROLE_HIERARCHY.get(min_role, 0)


@app.context_processor
def inject_user_context():
    return {"user": get_user(), "roles": get_roles(), "has_role": has_role}


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
    return auth0.authorize_redirect(redirect_uri=os.getenv("AUTH0_CALLBACK_URL"))


@app.route("/callback")
def callback():
    token = auth0.authorize_access_token()
    userinfo = token.get("userinfo", {})
    user_id = userinfo.get("sub", "")
    roles, error = get_user_roles(user_id) if user_id else ([], "no user_id")
    session["user"] = userinfo
    session["roles"] = roles
    session["_debug_error"] = error
    app.logger.info(f"Login - user: {userinfo.get('email')} | roles: {roles} | error: {error}")
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
    return render_template("sections/usuarios.html")


@app.route("/dashboard/config")
@login_required
def config():
    return render_template("sections/config.html")


@app.route("/api/user/roles")
@login_required
def api_user_roles():
    return jsonify({"roles": get_roles()})


@app.route("/debug/token")
@login_required
def debug_token():
    return jsonify({
        "session_roles": get_roles(),
        "email": get_user().get("email", ""),
        "user_id": get_user().get("sub", ""),
        "debug_error": session.get("_debug_error"),
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f"https://{AUTH0_DOMAIN}/v2/logout?"
        f"client_id={AUTH0_CLIENT_ID}&"
        f"returnTo={url_for('home', _external=True)}"
    )


if __name__ == "__main__":
    app.run(host="localhost", port=9900, debug=True)
