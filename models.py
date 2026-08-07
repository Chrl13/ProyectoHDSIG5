from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# ==========================================================
# BASE DE DATOS
# Inicializa SQLAlchemy para manejar los modelos del sistema
# ==========================================================

db = SQLAlchemy()

# Jerarquía de permisos de los usuarios
ROLE_HIERARCHY = {
    "admin": 3,
    "operator": 2,
    "viewer": 1
}

# ==========================================================
# MODELO DE ROLES
# Define los diferentes roles que puede tener un usuario
# ==========================================================

class Role(db.Model):

    __tablename__ = "roles"

    # Llave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Nombre del rol (admin, operator, viewer)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Nivel de permisos
    level = db.Column(db.Integer, nullable=False, default=1)

    # Descripción del rol
    description = db.Column(db.String(200), default="")

    # Relación con los usuarios
    users = db.relationship("User", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"

# ==========================================================
# MODELO DE USUARIOS
# Guarda la información de cada usuario autenticado
# ==========================================================

class User(db.Model):

    __tablename__ = "users"

    # Llave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Identificador único proporcionado por Auth0
    auth0_id = db.Column(
        db.String(128),
        unique=True,
        nullable=False,
        index=True
    )

    # Correo electrónico del usuario
    email = db.Column(db.String(256), nullable=False)

    # Nombre del usuario
    name = db.Column(db.String(256), default="")

    # Foto de perfil
    picture = db.Column(db.String(512), default="")

    # Rol asignado
    role_id = db.Column(
        db.Integer,
        db.ForeignKey("roles.id"),
        nullable=False
    )

    # Fecha de creación del registro
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Fecha de la última actualización
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<User {self.email} [{self.role.name if self.role else '?'}]>"

# ==========================================================
# MODELO DEL HISTORIAL DE CONSULTAS
# Guarda todas las consultas realizadas por los usuarios
# ==========================================================

class HistorialConsulta(db.Model):

    __tablename__ = "historial_consultas"

    # Llave primaria
    id = db.Column(db.Integer, primary_key=True)

    # Usuario que realizó la consulta
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Información de la ciudad consultada
    ciudad = db.Column(db.String(100), nullable=False)
    pais = db.Column(db.String(100), nullable=False)

    # Datos climáticos obtenidos desde la API
    temperatura = db.Column(db.Float)
    humedad = db.Column(db.Integer)
    viento = db.Column(db.Float)
    lluvia = db.Column(db.Float)

    # Tipo de consulta (Clima o Pronóstico)
    tipo_consulta = db.Column(
        db.String(20),
        nullable=False
    )

    # Fecha en que se realizó la consulta
    fecha_consulta = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    # Relación con el usuario
    usuario = db.relationship(
        "User",
        backref="historial"
    )

    def __repr__(self):
        return (
            f"<HistorialConsulta {self.ciudad} - "
            f"{self.tipo_consulta}>"
        )

# ==========================================================
# CREACIÓN DE ROLES POR DEFECTO
# Inserta los roles básicos al iniciar la aplicación
# ==========================================================

def seed_roles(app):

    with app.app_context():

        default_roles = [

            ("admin", 3, "Acceso total al sistema"),
            ("operator", 2, "Consulta y operaciones climaticas"),
            ("viewer", 1, "Solo lectura"),

        ]

        # Verificar si el rol ya existe antes de crearlo
        for name, level, desc in default_roles:

            if not Role.query.filter_by(name=name).first():

                db.session.add(
                    Role(
                        name=name,
                        level=level,
                        description=desc
                    )
                )

        # Guardar los cambios en la base de datos
        db.session.commit()