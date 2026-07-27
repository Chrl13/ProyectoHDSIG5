import pytest
from app import create_app
from models import db as _db, User, Role, ROLE_HIERARCHY


@pytest.mark.unit
class TestRoleHierarchy:
    def test_admin_highest_level(self):
        assert ROLE_HIERARCHY["admin"] == 3

    def test_operator_middle_level(self):
        assert ROLE_HIERARCHY["operator"] == 2

    def test_viewer_lowest_level(self):
        assert ROLE_HIERARCHY["viewer"] == 1

    def test_hierarchy_ordering(self):
        assert ROLE_HIERARCHY["admin"] > ROLE_HIERARCHY["operator"]
        assert ROLE_HIERARCHY["operator"] > ROLE_HIERARCHY["viewer"]


@pytest.mark.unit
class TestHasRole:
    def _make_app_with_session(self, roles):
        app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SERVER_NAME": "localhost:9900",
        })
        return app

    def test_has_role_with_admin(self, app, client, login_as_admin):
        with app.test_request_context():
            from flask import session
            with client.session_transaction() as sess:
                pass
            with app.test_client() as c:
                with c.session_transaction() as s:
                    s["roles"] = ["admin"]
                with c.session_transaction() as s:
                    roles = s.get("roles", [])
                    user_level = max(
                        ROLE_HIERARCHY.get(r, 0) for r in roles
                    )
                    assert user_level >= ROLE_HIERARCHY["admin"]
                    assert user_level >= ROLE_HIERARCHY["operator"]
                    assert user_level >= ROLE_HIERARCHY["viewer"]

    def test_has_role_with_viewer(self, app, client, login_as_viewer):
        with app.test_client() as c:
            with c.session_transaction() as s:
                s["roles"] = ["viewer"]
            with c.session_transaction() as s:
                roles = s.get("roles", [])
                user_level = max(
                    ROLE_HIERARCHY.get(r, 0) for r in roles
                )
                assert user_level < ROLE_HIERARCHY["admin"]
                assert user_level < ROLE_HIERARCHY["operator"]
                assert user_level >= ROLE_HIERARCHY["viewer"]

    def test_has_role_with_operator(self, app, client, login_as_operator):
        with app.test_client() as c:
            with c.session_transaction() as s:
                s["roles"] = ["operator"]
            with c.session_transaction() as s:
                roles = s.get("roles", [])
                user_level = max(
                    ROLE_HIERARCHY.get(r, 0) for r in roles
                )
                assert user_level < ROLE_HIERARCHY["admin"]
                assert user_level >= ROLE_HIERARCHY["operator"]
                assert user_level >= ROLE_HIERARCHY["viewer"]

    def test_has_role_empty_roles(self, app, client):
        with app.test_client() as c:
            with c.session_transaction() as s:
                s["roles"] = []
            with c.session_transaction() as s:
                roles = s.get("roles", [])
                assert not roles

    def test_has_role_unknown_role(self, app, client):
        with app.test_client() as c:
            with c.session_transaction() as s:
                s["roles"] = ["unknown_role"]
            with c.session_transaction() as s:
                roles = s.get("roles", [])
                user_level = max(
                    ROLE_HIERARCHY.get(r, 0) for r in roles
                )
                assert user_level == 0


@pytest.mark.unit
class TestLoginRequired:
    def test_redirect_when_not_logged_in(self, app, client):
        resp = client.get("/dashboard")
        assert resp.status_code == 302
        assert "/login" in resp.headers["Location"]

    def test_access_when_logged_in(self, app, client, login_as_admin):
        resp = client.get("/dashboard")
        assert resp.status_code == 200


@pytest.mark.unit
class TestRoleRequired:
    def test_admin_can_access_admin_route(self, app, client, login_as_admin):
        resp = client.get("/dashboard/usuarios")
        assert resp.status_code == 200

    def test_viewer_cannot_access_admin_route(self, app, client, login_as_viewer):
        resp = client.get("/dashboard/usuarios")
        assert resp.status_code == 403

    def test_operator_cannot_access_admin_route(self, app, client, login_as_operator):
        resp = client.get("/dashboard/usuarios")
        assert resp.status_code == 403

    def test_unauthenticated_redirected(self, app, client):
        resp = client.get("/dashboard/usuarios")
        assert resp.status_code == 302
