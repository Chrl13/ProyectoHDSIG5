import os
from functools import wraps
from flask import Flask, redirect, session, url_for, render_template, jsonify, request
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from models import db, User, Role, seed_roles, ROLE_HIERARCHY

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
    auth0_id = userinfo.get("sub", "")

    if not auth0_id:
        return redirect(url_for("login"))

    db_user = User.query.filter_by(auth0_id=auth0_id).first()

    if not db_user:
        has_admin = User.query.filter_by(role_id=Role.query.filter_by(name="admin").first().id).first()
        auto_role = Role.query.filter_by(name="admin").first() if not has_admin else Role.query.filter_by(name="viewer").first()
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
        has_admin = User.query.filter(User.role_id == admin_role.id, User.id != db_user.id).first()
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
    return render_template("sections/usuarios.html", all_users=all_users, all_roles=all_roles)


@app.route("/dashboard/config")
@login_required
def config():
    return render_template("sections/config.html")


@app.route("/api/user/roles")
@login_required
def api_user_roles():
    return jsonify({"roles": get_roles()})


@app.route("/api/users", methods=["GET"])
@login_required
@role_required("admin")
def api_list_users():
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "auth0_id": u.auth0_id,
        "email": u.email,
        "name": u.name,
        "role": u.role.name if u.role else "viewer",
        "role_id": u.role_id,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    } for u in users])


@app.route("/api/users/<int:user_id>/role", methods=["PUT"])
@login_required
@role_required("admin")
def api_update_user_role(user_id):
    data = request.get_json()
    role_id = data.get("role_id")

    if not role_id:
        return jsonify({"error": "role_id requerido"}), 400

    role = Role.query.get(role_id)
    if not role:
        return jsonify({"error": "Rol no encontrado"}), 404

    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    target_user.role_id = role_id
    db.session.commit()

    if session.get("db_user_id") == user_id:
        session["roles"] = [role.name]

    return jsonify({"ok": True, "user_id": user_id, "role": role.name})


@app.route("/api/roles", methods=["GET"])
@login_required
def api_list_roles():
    roles = Role.query.all()
    return jsonify([{"id": r.id, "name": r.name, "level": r.level, "description": r.description} for r in roles])


@app.route("/debug/token")
@login_required
def debug_token():
    return jsonify({
        "session_roles": get_roles(),
        "email": get_user().get("email", ""),
        "user_id": get_user().get("sub", ""),
        "db_user_id": session.get("db_user_id"),
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
