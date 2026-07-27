import json
import pytest
from unittest.mock import patch, MagicMock
from models import HistorialConsulta, User, Role, db


MOCK_GEO_RESPONSE = {
    "results": [
        {
            "name": "San Jose",
            "country": "Costa Rica",
            "latitude": 9.9281,
            "longitude": -84.0907,
        }
    ]
}

MOCK_CLIMA_RESPONSE = {
    "current": {
        "temperature_2m": 28.5,
        "relative_humidity_2m": 75,
        "apparent_temperature": 30.2,
        "precipitation": 0.0,
        "wind_speed_10m": 12.3,
    }
}

MOCK_PRONOSTICO_RESPONSE = {
    "daily": {
        "time": ["2026-07-20", "2026-07-21", "2026-07-22"],
        "temperature_2m_max": [30.0, 31.0, 29.0],
        "temperature_2m_min": [22.0, 23.0, 21.0],
        "weather_code": [1, 2, 3],
    }
}


@pytest.mark.integration
class TestApiClima:
    def test_clima_requires_auth(self, app, client):
        resp = client.get("/api/clima?ciudad=San+Jose")
        assert resp.status_code == 302

    def test_clima_missing_ciudad(self, app, client, login_as_admin):
        resp = client.get("/api/clima")
        assert resp.status_code == 400
        data = resp.get_json()
        assert "error" in data

    def test_clima_empty_ciudad(self, app, client, login_as_admin):
        resp = client.get("/api/clima?ciudad=")
        assert resp.status_code == 400

    def test_clima_city_not_found(self, app, client, login_as_admin):
        mock_geo = MagicMock()
        mock_geo.json.return_value = {}
        mock_geo.status_code = 200
        with patch("app.requests.get", return_value=mock_geo):
            resp = client.get("/api/clima?ciudad=FakeCity123")
            assert resp.status_code == 404

    @patch("app.requests.get")
    def test_clima_success(self, mock_get, app, client, login_as_admin):
        mock_geo = MagicMock()
        mock_geo.json.return_value = MOCK_GEO_RESPONSE
        mock_clima = MagicMock()
        mock_clima.json.return_value = MOCK_CLIMA_RESPONSE
        mock_get.side_effect = [mock_geo, mock_clima]

        resp = client.get("/api/clima?ciudad=San+Jose")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ciudad"] == "San Jose"
        assert data["pais"] == "Costa Rica"
        assert data["temperatura"] == 28.5
        assert data["humedad"] == 75
        assert data["viento"] == 12.3
        assert data["lluvia"] == 0.0

    @patch("app.requests.get")
    def test_clima_creates_historial(self, mock_get, app, client, login_as_admin, admin_user):
        mock_geo = MagicMock()
        mock_geo.json.return_value = MOCK_GEO_RESPONSE
        mock_clima = MagicMock()
        mock_clima.json.return_value = MOCK_CLIMA_RESPONSE
        mock_get.side_effect = [mock_geo, mock_clima]

        count_before = HistorialConsulta.query.filter_by(
            user_id=admin_user.id
        ).count()

        client.get("/api/clima?ciudad=San+Jose")

        count_after = HistorialConsulta.query.filter_by(
            user_id=admin_user.id
        ).count()
        assert count_after == count_before + 1

    @patch("app.requests.get")
    def test_clima_historial_data_correct(self, mock_get, app, client, login_as_admin, admin_user):
        mock_geo = MagicMock()
        mock_geo.json.return_value = MOCK_GEO_RESPONSE
        mock_clima = MagicMock()
        mock_clima.json.return_value = MOCK_CLIMA_RESPONSE
        mock_get.side_effect = [mock_geo, mock_clima]

        client.get("/api/clima?ciudad=San+Jose")

        consulta = (
            HistorialConsulta.query
            .filter_by(user_id=admin_user.id)
            .order_by(HistorialConsulta.fecha_consulta.desc())
            .first()
        )
        assert consulta.ciudad == "San Jose"
        assert consulta.pais == "Costa Rica"
        assert consulta.temperatura == 28.5
        assert consulta.humedad == 75
        assert consulta.tipo_consulta == "Clima"

    @patch("app.requests.get")
    def test_clima_api_error(self, mock_get, app, client, login_as_admin):
        mock_get.side_effect = Exception("API Error")
        resp = client.get("/api/clima?ciudad=San+Jose")
        assert resp.status_code == 500
        data = resp.get_json()
        assert "error" in data


@pytest.mark.integration
class TestApiHistorial:
    def test_historial_requires_auth(self, app, client):
        resp = client.get("/api/historial")
        assert resp.status_code == 302

    def test_historial_empty(self, app, client, login_as_admin, admin_user):
        resp = client.get("/api/historial")
        assert resp.status_code == 200
        data = resp.get_json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_historial_with_data(
        self, app, client, login_as_admin, admin_user, sample_historial
    ):
        resp = client.get("/api/historial")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 3

    def test_historial_ordered_by_date_desc(
        self, app, client, login_as_admin, admin_user, sample_historial
    ):
        resp = client.get("/api/historial")
        data = resp.get_json()
        dates = [entry["fecha"] for entry in data]
        assert dates == sorted(dates, reverse=True)

    def test_historial_structure(
        self, app, client, login_as_admin, admin_user, sample_historial
    ):
        resp = client.get("/api/historial")
        data = resp.get_json()
        for entry in data:
            assert "fecha" in entry
            assert "usuario" in entry
            assert "accion" in entry
            assert "ciudad" in entry
            assert "pais" in entry
            assert "tipo" in entry

    def test_historial_clima_action_label(
        self, app, client, login_as_admin, admin_user, sample_historial
    ):
        resp = client.get("/api/historial")
        data = resp.get_json()
        clima_entries = [e for e in data if e["tipo"] == "Clima"]
        for entry in clima_entries:
            assert entry["accion"] == "Consultó el clima"

    def test_historial_pronostico_action_label(
        self, app, client, login_as_admin, admin_user, sample_historial
    ):
        resp = client.get("/api/historial")
        data = resp.get_json()
        pron_entries = [e for e in data if e["tipo"] == "Pronostico"]
        for entry in pron_entries:
            assert entry["accion"] == "Consultó el pronóstico"

    def test_historial_only_own_data(
        self, app, client, login_as_admin, admin_user, viewer_user, sample_historial
    ):
        other_consulta = HistorialConsulta(
            user_id=viewer_user.id,
            ciudad="Limon",
            pais="Costa Rica",
            tipo_consulta="Clima",
        )
        db.session.add(other_consulta)
        db.session.commit()

        from tests.conftest import _login_user
        _login_user(client, viewer_user)
        resp = client.get("/api/historial")
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]["ciudad"] == "Limon"


@pytest.mark.integration
class TestApiPronostico:
    def test_pronostico_requires_auth(self, app, client):
        resp = client.get("/api/pronostico?ciudad=San+Jose")
        assert resp.status_code == 302

    def test_pronostico_missing_ciudad(self, app, client, login_as_admin):
        resp = client.get("/api/pronostico")
        assert resp.status_code == 400

    @patch("app.requests.get")
    def test_pronostico_success(self, mock_get, app, client, login_as_admin):
        mock_geo = MagicMock()
        mock_geo.json.return_value = MOCK_GEO_RESPONSE
        mock_forecast = MagicMock()
        mock_forecast.json.return_value = MOCK_PRONOSTICO_RESPONSE
        mock_get.side_effect = [mock_geo, mock_forecast]

        resp = client.get("/api/pronostico?ciudad=San+Jose")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["ciudad"] == "San Jose"
        assert len(data["dias"]) == 3

    @patch("app.requests.get")
    def test_pronostico_api_error(self, mock_get, app, client, login_as_admin):
        mock_get.side_effect = Exception("Connection error")
        resp = client.get("/api/pronostico?ciudad=San+Jose")
        assert resp.status_code == 500
