from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

ROLE_HIERARCHY = {"admin": 3, "operator": 2, "viewer": 1}


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    level = db.Column(db.Integer, nullable=False, default=1)
    description = db.Column(db.String(200), default="")

    users = db.relationship("User", backref="role", lazy=True)

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    auth0_id = db.Column(db.String(128), unique=True, nullable=False, index=True)
    email = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(256), default="")
    picture = db.Column(db.String(512), default="")
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<User {self.email} [{self.role.name if self.role else '?'}]>"


def seed_roles(app):
    with app.app_context():
        default_roles = [
            ("admin", 3, "Acceso total al sistema"),
            ("operator", 2, "Consulta y operaciones climaticas"),
            ("viewer", 1, "Solo lectura"),
        ]
        for name, level, desc in default_roles:
            if not Role.query.filter_by(name=name).first():
                db.session.add(Role(name=name, level=level, description=desc))
        db.session.commit()
