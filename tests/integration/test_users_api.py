import json
import pytest
from models import User, Role, db


@pytest.mark.integration
class TestApiListUsers:
    def test_list_users_requires_auth(self, app, client):
        resp = client.get("/api/users")
        assert resp.status_code == 302

    def test_list_users_requires_admin(self, app, client, login_as_viewer):
        resp = client.get("/api/users")
        assert resp.status_code == 403

    def test_list_users_returns_list_type(self, app, client, login_as_admin):
        resp = client.get("/api/users")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)

    def test_list_users_returns_data(self, app, client, login_as_admin, admin_user):
        resp = client.get("/api/users")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["email"] == "admin@test.com"
        assert data[0]["auth0_id"] == "auth0|test_admin_001"
        assert data[0]["role"] == "admin"

    def test_list_users_multiple(self, app, client, login_as_admin, admin_user, viewer_user):
        resp = client.get("/api/users")
        data = resp.get_json()
        assert len(data) == 2
        emails = {u["email"] for u in data}
        assert "admin@test.com" in emails
        assert "viewer@test.com" in emails

    def test_list_users_includes_created_at(self, app, client, login_as_admin, admin_user):
        resp = client.get("/api/users")
        data = resp.get_json()
        assert data[0]["created_at"] is not None


@pytest.mark.integration
class TestApiUpdateUserRole:
    def test_update_role_requires_auth(self, app, client):
        resp = client.put(
            "/api/users/1/role",
            json={"role_id": 2},
        )
        assert resp.status_code == 302

    def test_update_role_requires_admin(self, app, client, login_as_viewer, viewer_user):
        resp = client.put(
            f"/api/users/{viewer_user.id}/role",
            json={"role_id": 3},
        )
        assert resp.status_code == 403

    def test_update_role_missing_role_id(self, app, client, login_as_admin, viewer_user):
        resp = client.put(
            f"/api/users/{viewer_user.id}/role",
            json={},
            content_type="application/json",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_update_role_invalid_role(self, app, client, login_as_admin, viewer_user):
        resp = client.put(
            f"/api/users/{viewer_user.id}/role",
            json={"role_id": 999},
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_update_role_user_not_found(self, app, client, login_as_admin):
        resp = client.put(
            "/api/users/9999/role",
            json={"role_id": 1},
            content_type="application/json",
        )
        assert resp.status_code == 404

    def test_update_role_success(self, app, client, login_as_admin, viewer_user):
        operator_role = Role.query.filter_by(name="operator").first()
        resp = client.put(
            f"/api/users/{viewer_user.id}/role",
            json={"role_id": operator_role.id},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ok"] is True
        assert data["role"] == "operator"
        assert data["user_id"] == viewer_user.id

    def test_update_role_persists(self, app, client, login_as_admin, viewer_user):
        operator_role = Role.query.filter_by(name="operator").first()
        client.put(
            f"/api/users/{viewer_user.id}/role",
            json={"role_id": operator_role.id},
            content_type="application/json",
        )
        updated_user = User.query.get(viewer_user.id)
        assert updated_user.role_id == operator_role.id

    def test_update_own_role_updates_session(self, app, client, login_as_admin, admin_user):
        viewer_role = Role.query.filter_by(name="viewer").first()
        resp = client.put(
            f"/api/users/{admin_user.id}/role",
            json={"role_id": viewer_role.id},
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["role"] == "viewer"


@pytest.mark.integration
class TestApiListRoles:
    def test_list_roles_requires_auth(self, app, client):
        resp = client.get("/api/roles")
        assert resp.status_code == 302

    def test_list_roles_returns_three(self, app, client, login_as_admin):
        resp = client.get("/api/roles")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 3

    def test_list_roles_structure(self, app, client, login_as_admin):
        resp = client.get("/api/roles")
        data = resp.get_json()
        for role in data:
            assert "id" in role
            assert "name" in role
            assert "level" in role
            assert "description" in role

    def test_list_roles_viewer_can_access(self, app, client, login_as_viewer):
        resp = client.get("/api/roles")
        assert resp.status_code == 200


@pytest.mark.integration
class TestApiUserRoles:
    def test_user_roles_requires_auth(self, app, client):
        resp = client.get("/api/user/roles")
        assert resp.status_code == 302

    def test_user_roles_returns_session_roles(self, app, client, login_as_admin):
        resp = client.get("/api/user/roles")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "roles" in data
        assert "admin" in data["roles"]

    def test_user_roles_viewer(self, app, client, login_as_viewer):
        resp = client.get("/api/user/roles")
        data = resp.get_json()
        assert "viewer" in data["roles"]
