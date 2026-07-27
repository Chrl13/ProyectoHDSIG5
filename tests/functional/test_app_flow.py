import pytest
import threading
import time
import requests as http_requests

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False


def _create_session_cookie(app, session_data):
    from flask.sessions import SecureCookieSessionInterface
    with app.test_request_context():
        session_interface = SecureCookieSessionInterface()
        signer = session_interface.get_signing_serializer(app)
        return signer.dumps(session_data)


def _start_server(app, port=9901):
    server_thread = threading.Thread(
        target=lambda: app.run(
            host="127.0.0.1",
            port=port,
            use_reloader=False,
            debug=False,
        ),
        daemon=True,
    )
    server_thread.start()
    for _ in range(20):
        try:
            http_requests.get(f"http://127.0.0.1:{port}/", timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    return server_thread


@pytest.fixture(scope="module")
def server(app):
    _start_server(app, port=9901)
    yield app


@pytest.fixture(scope="module")
def driver():
    if not SELENIUM_AVAILABLE:
        pytest.skip("Selenium not installed")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    d = webdriver.Chrome(options=options)
    d.set_page_load_timeout(10)
    yield d
    d.quit()


@pytest.mark.functional
class TestHomePage:
    def test_home_page_loads(self, server, driver):
        driver.get("http://127.0.0.1:9901/")
        time.sleep(0.5)
        body = driver.page_source.lower()
        assert "climapp" in body or "clima" in body

    def test_home_has_login_button(self, server, driver):
        driver.get("http://127.0.0.1:9901/")
        time.sleep(0.5)
        body = driver.page_source.lower()
        assert "login" in body or "iniciar" in body or "auth0" in body

    def test_home_title(self, server, driver):
        driver.get("http://127.0.0.1:9901/")
        time.sleep(0.5)
        assert driver.title is not None

    def test_home_has_css_styles(self, server, driver):
        driver.get("http://127.0.0.1:9901/")
        time.sleep(0.5)
        stylesheets = driver.find_elements(By.TAG_NAME, "link")
        has_css = any(
            "css" in s.get_attribute("rel") or "css" in (s.get_attribute("href") or "")
            for s in stylesheets
        )
        assert has_css


@pytest.mark.functional
class TestAuthenticationRedirects:
    def test_dashboard_redirects_when_not_logged_in(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)
        location = resp.headers.get("Location", "")
        assert "login" in location.lower()

    def test_clima_redirects_when_not_logged_in(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard/clima",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)
        location = resp.headers.get("Location", "")
        assert "login" in location.lower()

    def test_historial_redirects_when_not_logged_in(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard/clima/historial",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)
        location = resp.headers.get("Location", "")
        assert "login" in location.lower()

    def test_usuarios_redirects_when_not_logged_in(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard/usuarios",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)

    def test_pronostico_redirects_when_not_logged_in(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard/clima/pronostico",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)

    def test_config_redirects_when_not_logged_in(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard/config",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)


@pytest.mark.functional
class TestAuthenticatedPages:
    def _login_via_cookie(self, server, driver, user):
        cookie = _create_session_cookie(server, {
            "user": {
                "sub": user.auth0_id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
            },
            "roles": [user.role.name] if user.role else [],
            "db_user_id": user.id,
        })
        driver.get("http://127.0.0.1:9901/")
        time.sleep(0.5)
        driver.add_cookie({
            "name": "session",
            "value": cookie,
            "domain": "127.0.0.1",
            "path": "/",
        })

    def test_dashboard_loads_when_authenticated(
        self, server, driver, admin_user
    ):
        self._login_via_cookie(server, driver, admin_user)
        driver.get("http://127.0.0.1:9901/dashboard")
        time.sleep(1.0)
        assert "/dashboard" in driver.current_url

    def test_sidebar_present_when_authenticated(
        self, server, driver, admin_user
    ):
        self._login_via_cookie(server, driver, admin_user)
        driver.get("http://127.0.0.1:9901/dashboard")
        time.sleep(1.0)
        body = driver.page_source.lower()
        assert "dashboard" in body or "panel" in body

    def test_usuarios_page_loads_for_admin(
        self, server, driver, admin_user
    ):
        self._login_via_cookie(server, driver, admin_user)
        driver.get("http://127.0.0.1:9901/dashboard/usuarios")
        time.sleep(1.0)
        assert "/usuarios" in driver.current_url

    def test_usuarios_page_forbidden_for_viewer(
        self, server, driver, viewer_user
    ):
        self._login_via_cookie(server, driver, viewer_user)
        driver.get("http://127.0.0.1:9901/dashboard/usuarios")
        time.sleep(1.0)
        body = driver.page_source.lower()
        assert "acceso" in body or "403" in body or "denegado" in body

    def test_clima_page_loads_when_authenticated(
        self, server, driver, admin_user
    ):
        self._login_via_cookie(server, driver, admin_user)
        driver.get("http://127.0.0.1:9901/dashboard/clima")
        time.sleep(1.0)
        assert "/clima" in driver.current_url


def _login_via_cookie(server, driver, user):
    cookie = _create_session_cookie(server, {
        "user": {
            "sub": user.auth0_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        },
        "roles": [user.role.name] if user.role else [],
        "db_user_id": user.id,
    })
    driver.get("http://127.0.0.1:9901/")
    time.sleep(0.5)
    driver.add_cookie({
        "name": "session",
        "value": cookie,
        "domain": "127.0.0.1",
        "path": "/",
    })


@pytest.mark.functional
class TestLogout:
    def test_logout_clears_session(self, server, driver, admin_user):
        _login_via_cookie(server, driver, admin_user)
        driver.get("http://127.0.0.1:9901/dashboard")
        time.sleep(0.5)
        driver.get("http://127.0.0.1:9901/logout")
        time.sleep(0.5)

        resp = http_requests.get(
            "http://127.0.0.1:9901/dashboard",
            allow_redirects=False,
            cookies={c["name"]: c["value"] for c in driver.get_cookies()},
        )
        assert resp.status_code in (301, 302)

    def test_logout_redirects_to_home(self, server):
        resp = http_requests.get(
            "http://127.0.0.1:9901/logout",
            allow_redirects=False,
        )
        assert resp.status_code in (301, 302)
        location = resp.headers.get("Location", "")
        assert "/" in location
