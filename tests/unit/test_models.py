import pytest
from datetime import datetime, timezone
from models import User, Role, HistorialConsulta, db


@pytest.mark.unit
class TestRoleModel:
    def test_create_role(self, db_session):
        role = Role(name="test_role", level=2, description="Test role")
        db_session.add(role)
        db_session.commit()
        assert role.id is not None
        assert role.name == "test_role"
        assert role.level == 2
        assert role.description == "Test role"

    def test_role_name_unique(self, db_session):
        role1 = Role(name="unique_role", level=1)
        role2 = Role(name="unique_role", level=2)
        db_session.add(role1)
        db_session.commit()
        db_session.add(role2)
        with pytest.raises(Exception):
            db_session.commit()

    def test_role_default_level(self, db_session):
        role = Role(name="default_level_role")
        db_session.add(role)
        db_session.commit()
        assert role.level == 1

    def test_role_default_description(self, db_session):
        role = Role(name="default_desc_role", level=1)
        db_session.add(role)
        db_session.commit()
        assert role.description == ""

    def test_role_repr(self, db_session):
        role = Role(name="test_repr_role", level=3)
        db_session.add(role)
        db_session.commit()
        assert repr(role) == "<Role test_repr_role>"

    def test_role_users_relationship(self, db_session):
        role = Role(name="rel_role", level=1)
        db_session.add(role)
        db_session.commit()
        user = User(
            auth0_id="auth0|rel_test",
            email="rel@test.com",
            name="Rel Test",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        assert len(role.users) == 1
        assert role.users[0].email == "rel@test.com"


@pytest.mark.unit
class TestUserModel:
    def test_create_user(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|test_user_001",
            email="test@example.com",
            name="Test User",
            picture="http://example.com/pic.jpg",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        assert user.id is not None
        assert user.auth0_id == "auth0|test_user_001"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.picture == "http://example.com/pic.jpg"
        assert user.role_id == role.id

    def test_user_auth0_id_unique(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user1 = User(
            auth0_id="auth0|duplicate",
            email="u1@test.com",
            role_id=role.id,
        )
        user2 = User(
            auth0_id="auth0|duplicate",
            email="u2@test.com",
            role_id=role.id,
        )
        db_session.add(user1)
        db_session.commit()
        db_session.add(user2)
        with pytest.raises(Exception):
            db_session.commit()

    def test_user_default_values(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|defaults",
            email="defaults@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        assert user.name == ""
        assert user.picture == ""
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_created_at_auto(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        before = datetime.now(timezone.utc)
        user = User(
            auth0_id="auth0|timestamp_test",
            email="ts@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        after = datetime.now(timezone.utc)
        assert before <= user.created_at.replace(tzinfo=timezone.utc) <= after

    def test_user_role_relationship(self, db_session):
        role = Role.query.filter_by(name="admin").first()
        user = User(
            auth0_id="auth0|role_rel",
            email="rolerel@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        assert user.role is not None
        assert user.role.name == "admin"

    def test_user_repr(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|repr_test",
            email="repr@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        assert "repr@test.com" in repr(user)
        assert "viewer" in repr(user)

    def test_user_historial_relationship(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|hist_rel",
            email="histrel@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()
        consulta = HistorialConsulta(
            user_id=user.id,
            ciudad="Test City",
            pais="Test Country",
            temperatura=25.0,
            humedad=60,
            viento=10.0,
            lluvia=0.0,
            tipo_consulta="Clima",
        )
        db_session.add(consulta)
        db_session.commit()
        assert len(user.historial) == 1
        assert user.historial[0].ciudad == "Test City"


@pytest.mark.unit
class TestHistorialConsultaModel:
    def test_create_historial(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|hist_create",
            email="histcreate@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()

        consulta = HistorialConsulta(
            user_id=user.id,
            ciudad="Cartago",
            pais="Costa Rica",
            temperatura=22.5,
            humedad=80,
            viento=5.0,
            lluvia=10.0,
            tipo_consulta="Clima",
        )
        db_session.add(consulta)
        db_session.commit()
        assert consulta.id is not None
        assert consulta.ciudad == "Cartago"
        assert consulta.pais == "Costa Rica"
        assert consulta.temperatura == 22.5
        assert consulta.humedad == 80
        assert consulta.viento == 5.0
        assert consulta.lluvia == 10.0
        assert consulta.tipo_consulta == "Clima"

    def test_historial_fecha_auto(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|hist_fecha",
            email="histfecha@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()

        before = datetime.now(timezone.utc)
        consulta = HistorialConsulta(
            user_id=user.id,
            ciudad="Heredia",
            pais="Costa Rica",
            tipo_consulta="Clima",
        )
        db_session.add(consulta)
        db_session.commit()
        after = datetime.now(timezone.utc)
        assert consulta.fecha_consulta is not None

    def test_historial_user_relationship(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|hist_user_rel",
            email="histuserrel@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()

        consulta = HistorialConsulta(
            user_id=user.id,
            ciudad="Alajuela",
            pais="Costa Rica",
            tipo_consulta="Clima",
        )
        db_session.add(consulta)
        db_session.commit()
        assert consulta.usuario is not None
        assert consulta.usuario.email == "histuserrel@test.com"

    def test_historial_repr(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|hist_repr",
            email="histrepr@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()

        consulta = HistorialConsulta(
            user_id=user.id,
            ciudad="Puntarenas",
            pais="Costa Rica",
            tipo_consulta="Clima",
        )
        db_session.add(consulta)
        db_session.commit()
        r = repr(consulta)
        assert "Puntarenas" in r
        assert "Clima" in r

    def test_historial_nullable_fields(self, db_session):
        role = Role.query.filter_by(name="viewer").first()
        user = User(
            auth0_id="auth0|hist_nullable",
            email="histnullable@test.com",
            role_id=role.id,
        )
        db_session.add(user)
        db_session.commit()

        consulta = HistorialConsulta(
            user_id=user.id,
            ciudad="Liberia",
            pais="Costa Rica",
            tipo_consulta="Pronostico",
        )
        db_session.add(consulta)
        db_session.commit()
        assert consulta.temperatura is None
        assert consulta.humedad is None
        assert consulta.viento is None
        assert consulta.lluvia is None


@pytest.mark.unit
class TestSeedRoles:
    def test_seed_creates_three_roles(self, db_session):
        roles = Role.query.all()
        names = {r.name for r in roles}
        assert "admin" in names
        assert "operator" in names
        assert "viewer" in names
        assert len(roles) == 3

    def test_seed_admin_level(self, db_session):
        admin = Role.query.filter_by(name="admin").first()
        assert admin.level == 3

    def test_seed_operator_level(self, db_session):
        operator = Role.query.filter_by(name="operator").first()
        assert operator.level == 2

    def test_seed_viewer_level(self, db_session):
        viewer = Role.query.filter_by(name="viewer").first()
        assert viewer.level == 1

    def test_seed_idempotent(self, db_session, app):
        from models import seed_roles
        seed_roles(app)
        roles = Role.query.all()
        assert len(roles) == 3
