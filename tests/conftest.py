import os
import sys
import pytest
from datetime import datetime, timezone

os.environ.setdefault("AUTH0_CLIENT_ID", "test_client_id")
os.environ.setdefault("AUTH0_CLIENT_SECRET", "test_client_secret")
os.environ.setdefault("AUTH0_DOMAIN", "test.auth0.com")
os.environ.setdefault("AUTH0_CALLBACK_URL", "http://localhost:9900/callback")
os.environ.setdefault("SECRET_KEY", "test_secret_key_for_testing")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db as _db, User, Role, HistorialConsulta

SCREENSHOTS_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "reports", "screenshots"
)
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)


@pytest.fixture(scope="session")
def app():
    application = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
        "SERVER_NAME": "localhost:9900",
    })
    yield application


@pytest.fixture(autouse=True)
def setup_database(app):
    with app.app_context():
        _db.create_all()
        _seed_test_roles()
        yield
        _db.session.remove()
        _db.drop_all()


def _seed_test_roles():
    default_roles = [
        ("admin", 3, "Acceso total al sistema"),
        ("operator", 2, "Consulta y operaciones climaticas"),
        ("viewer", 1, "Solo lectura"),
    ]
    for name, level, desc in default_roles:
        if not Role.query.filter_by(name=name).first():
            _db.session.add(Role(name=name, level=level, description=desc))
    _db.session.commit()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def db_session(app):
    with app.app_context():
        yield _db.session


@pytest.fixture
def admin_user(db_session):
    role = Role.query.filter_by(name="admin").first()
    user = User(
        auth0_id="auth0|test_admin_001",
        email="admin@test.com",
        name="Test Admin",
        picture="",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def viewer_user(db_session):
    role = Role.query.filter_by(name="viewer").first()
    user = User(
        auth0_id="auth0|test_viewer_001",
        email="viewer@test.com",
        name="Test Viewer",
        picture="",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def operator_user(db_session):
    role = Role.query.filter_by(name="operator").first()
    user = User(
        auth0_id="auth0|test_operator_001",
        email="operator@test.com",
        name="Test Operator",
        picture="",
        role_id=role.id,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _login_user(client, user):
    with client.session_transaction() as sess:
        sess["user"] = {
            "sub": user.auth0_id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture,
        }
        sess["roles"] = [user.role.name] if user.role else []
        sess["db_user_id"] = user.id


@pytest.fixture
def login_as_admin(client, admin_user):
    _login_user(client, admin_user)
    return admin_user


@pytest.fixture
def login_as_viewer(client, viewer_user):
    _login_user(client, viewer_user)
    return viewer_user


@pytest.fixture
def login_as_operator(client, operator_user):
    _login_user(client, operator_user)
    return operator_user


@pytest.fixture
def sample_historial(db_session, admin_user):
    consultas = [
        HistorialConsulta(
            user_id=admin_user.id,
            ciudad="San Jose",
            pais="Costa Rica",
            temperatura=28.5,
            humedad=75,
            viento=12.3,
            lluvia=0.0,
            tipo_consulta="Clima",
            fecha_consulta=datetime(2026, 7, 20, 10, 0, 0, tzinfo=timezone.utc),
        ),
        HistorialConsulta(
            user_id=admin_user.id,
            ciudad="Limon",
            pais="Costa Rica",
            temperatura=31.0,
            humedad=85,
            viento=8.5,
            lluvia=5.2,
            tipo_consulta="Clima",
            fecha_consulta=datetime(2026, 7, 21, 14, 30, 0, tzinfo=timezone.utc),
        ),
        HistorialConsulta(
            user_id=admin_user.id,
            ciudad="San Jose",
            pais="Costa Rica",
            temperatura=26.0,
            humedad=70,
            viento=15.0,
            lluvia=0.0,
            tipo_consulta="Pronostico",
            fecha_consulta=datetime(2026, 7, 22, 8, 0, 0, tzinfo=timezone.utc),
        ),
    ]
    for c in consultas:
        db_session.add(c)
    db_session.commit()
    return consultas


@pytest.fixture
def screenshot(driver, request):
    """Fixture that provides screenshot capability for Selenium tests.

    Automatically captures:
    - A screenshot at the start of the test
    - A screenshot at the end of the test (success)
    - A screenshot on failure (before closing)

    Also exposes a capture() method for manual screenshots at any point.
    """
    test_name = request.node.name
    class_name = request.node.cls.__name__ if request.node.cls else "standalone"
    prefix = f"{class_name}__{test_name}"

    def capture(label):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}__{label}__{timestamp}.png"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        driver.save_screenshot(filepath)
        return filepath

    capture(f"01_inicio")
    yield capture

    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        capture("99_fallo")
    else:
        capture("02_fin_exitoso")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    import pytest
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
