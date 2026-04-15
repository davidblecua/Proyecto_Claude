"""
Configuración de tests para RentaMaq.

Usa SQLite en memoria para aislar completamente los tests de cualquier base
de datos real (desarrollo, preproducción o producción).

El truco consiste en parchear app.db.database.engine ANTES de importar
app.main, de modo que la llamada a Base.metadata.create_all() de main.py
use el engine de SQLite en lugar del de PostgreSQL.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# ── 1. Importar database.py para que esté en sys.modules ────────────────────
import app.db.database as _db_module

# ── 2. Crear engine SQLite en memoria ────────────────────────────────────────
# StaticPool es obligatorio para que TestClient (otro hilo) comparta la misma
# base de datos en memoria que creó el hilo principal.
_SQLITE_URL = "sqlite:///:memory:"
_test_engine = create_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# ── 3. Parchear el módulo ANTES de importar app.main ─────────────────────────
# app.main hace: from app.db.database import engine, Base
# Al haber parchado engine aquí, main.py recibirá _test_engine
_db_module.engine = _test_engine
_db_module.SessionLocal = _TestSessionLocal

# ── 4. Registrar todos los modelos en Base.metadata ──────────────────────────
from app.models import user as _u                   # noqa: E402
from app.models import machinery as _m              # noqa: E402
from app.models import booking as _b                # noqa: E402
from app.models import message as _msg              # noqa: E402
from app.models import operator as _op              # noqa: E402
from app.models import machinery_request as _req    # noqa: E402
from app.models import review as _rev               # noqa: E402
from app.db.database import Base                    # noqa: E402

# ── 5. Crear tablas en SQLite ─────────────────────────────────────────────────
Base.metadata.create_all(bind=_test_engine)

# ── 6. Importar la app (ya con engine parchado) ───────────────────────────────
from app.main import app          # noqa: E402
from app.db.database import get_db  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def db():
    """
    Sesión de base de datos aislada por test.
    Al finalizar cada test se eliminan todos los datos para garantizar
    que los tests sean independientes entre sí.
    """
    session = _TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Limpiar todas las tablas tras cada test (orden inverso por FK)
        with _test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                conn.execute(table.delete())


@pytest.fixture(scope="function")
def client(db):
    """
    TestClient de FastAPI con la dependencia get_db sobreescrita para
    usar la sesión SQLite de test en lugar de la de producción.
    """
    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()
