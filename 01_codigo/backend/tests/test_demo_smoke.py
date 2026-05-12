"""
Smoke test del flujo demo de RentaMaq.

Verifica el recorrido completo sin dependencias externas ni Playwright:
  1. Registro y login de propietario (david)
  2. Publicar maquinaria con fotos
  3. Buscar maquinaria como cliente
  4. Reservar → ver reserva
  5. Enviar mensaje propietario↔cliente
  6. Ver panel de propietario

Usa TestClient con SQLite en memoria (misma infraestructura que el resto de tests).
"""
import io
import json
import pytest
from datetime import date, timedelta

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL    = "/api/v1/auth/login"
MACHINERY_URL = "/api/v1/machinery"
BOOKINGS_URL  = "/api/v1/bookings"
MESSAGES_URL  = "/api/v1/messages"

# ── Datos demo ────────────────────────────────────────────────────────────────

DAVID = {
    "email": "david@demo.com",
    "username": "david_demo",
    "password": "Demo1234!",
    "role": "publisher",
    "full_name": "David Demo",
    "company_name": "Maquinaria Demo SL",
    "location_city": "Lleida",
    "location_province": "Lleida",
}

CLIENTE = {
    "email": "cliente@demo.com",
    "username": "cliente_demo",
    "password": "Demo1234!",
    "role": "consumer",
    "full_name": "Cliente Demo",
}

MACHINE_PAYLOAD = {
    "title": "Excavadora Caterpillar 320",
    "description": "Excavadora hidráulica de 20 toneladas para obra civil y demolición.",
    "machinery_type": "excavadora",
    "daily_rate": 250.0,
    "location_city": "Lleida",
    "location_province": "Lleida",
    "requires_operator": False,
    "delivery_available": True,
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _register_and_login(client, data: dict) -> str:
    client.post(REGISTER_URL, json=data)
    r = client.post(LOGIN_URL, json={"email": data["email"], "password": data["password"]})
    assert r.status_code == 200, f"login failed: {r.text}"
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _fake_jpeg(size: int = 512) -> bytes:
    header = b'\xff\xd8\xff\xe0' + b'\x00' * 12
    return header + b'\x00' * max(0, size - len(header))


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestDemoFlow:
    """Recorre el flujo demo completo en orden."""

    def test_01_propietario_publica_maquinaria(self, client, mock_storage):
        token = _register_and_login(client, DAVID)

        # Crear maquina
        r = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(token))
        assert r.status_code == 201, r.text
        machine = r.json()
        assert machine["title"] == MACHINE_PAYLOAD["title"]
        assert machine["owner_id"] is not None

    def test_02_propietario_sube_fotos(self, client, mock_storage):
        token = _register_and_login(client, DAVID)
        r = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(token))
        machine_id = r.json()["id"]

        photos_url = f"{MACHINERY_URL}/{machine_id}/photos"
        file_data = [("files", ("photo1.jpg", io.BytesIO(_fake_jpeg()), "image/jpeg"))]
        r2 = client.post(photos_url, files=file_data, headers=_auth(token))
        assert r2.status_code == 200, r2.text
        images = json.loads(r2.json()["images"]) if isinstance(r2.json()["images"], str) else r2.json()["images"]
        assert len(images) >= 1

    def test_03_cliente_busca_maquinaria(self, client, mock_storage):
        # Propietario publica
        david_token = _register_and_login(client, DAVID)
        client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token))

        # Cliente busca
        _register_and_login(client, CLIENTE)
        r = client.get(f"{MACHINERY_URL}/search?location_province=Lleida")
        assert r.status_code == 200, r.text
        data = r.json()
        assert data["total"] >= 1
        assert data["machinery"][0]["location_province"] == "Lleida"

    def test_04_cliente_reserva_maquinaria(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        machine = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token)).json()

        cliente_token = _register_and_login(client, CLIENTE)
        start = (date.today() + timedelta(days=5)).isoformat() + "T00:00:00"
        end   = (date.today() + timedelta(days=7)).isoformat() + "T00:00:00"
        booking_payload = {
            "machinery_id": machine["id"],
            "start_date": start,
            "end_date": end,
        }
        r = client.post(BOOKINGS_URL, json=booking_payload, headers=_auth(cliente_token))
        assert r.status_code == 201, r.text
        booking = r.json()
        assert booking["machinery_id"] == machine["id"]
        assert booking["status"] in ("pending", "confirmed")

    def test_05_cliente_ve_sus_reservas(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        machine = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token)).json()

        cliente_token = _register_and_login(client, CLIENTE)
        start = (date.today() + timedelta(days=10)).isoformat() + "T00:00:00"
        end   = (date.today() + timedelta(days=12)).isoformat() + "T00:00:00"
        client.post(BOOKINGS_URL, json={"machinery_id": machine["id"], "start_date": start, "end_date": end},
                    headers=_auth(cliente_token))

        r = client.get(f"{BOOKINGS_URL}/my-bookings", headers=_auth(cliente_token))
        assert r.status_code == 200, r.text
        assert len(r.json()) >= 1

    def test_06_cliente_envia_mensaje_al_propietario(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        machine = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token)).json()

        # Obtener id de david
        me_r = client.get("/api/v1/users/me", headers=_auth(david_token))
        assert me_r.status_code == 200, me_r.text
        david_id = me_r.json()["id"]

        cliente_token = _register_and_login(client, CLIENTE)
        payload = {
            "receiver_id": david_id,
            "machinery_id": machine["id"],
            "content": "Hola, ¿está disponible la excavadora esta semana?",
        }
        r = client.post(MESSAGES_URL, json=payload, headers=_auth(cliente_token))
        assert r.status_code == 201, r.text
        assert r.json()["content"] == payload["content"]

    def test_07_propietario_ve_sus_maquinas(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token))

        r = client.get(f"{MACHINERY_URL}/my/machinery", headers=_auth(david_token))
        assert r.status_code == 200, r.text
        assert len(r.json()) >= 1

    def test_08_propietario_edita_maquinaria(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        machine = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token)).json()

        r = client.put(
            f"{MACHINERY_URL}/{machine['id']}",
            json={"daily_rate": 280.0},
            headers=_auth(david_token),
        )
        assert r.status_code == 200, r.text
        assert r.json()["daily_rate"] == 280.0

    def test_09_busqueda_por_tipo(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token))

        r = client.get(f"{MACHINERY_URL}/search?machinery_type=excavadora")
        assert r.status_code == 200, r.text
        items = r.json()["machinery"]
        assert all(i["machinery_type"] == "excavadora" for i in items)

    def test_10_detalle_maquinaria_incluye_fotos(self, client, mock_storage):
        david_token = _register_and_login(client, DAVID)
        machine = client.post(MACHINERY_URL, json=MACHINE_PAYLOAD, headers=_auth(david_token)).json()

        photos_url = f"{MACHINERY_URL}/{machine['id']}/photos"
        client.post(
            photos_url,
            files=[("files", ("img.jpg", io.BytesIO(_fake_jpeg()), "image/jpeg"))],
            headers=_auth(david_token),
        )

        r = client.get(f"{MACHINERY_URL}/{machine['id']}")
        assert r.status_code == 200, r.text
        images = r.json().get("images")
        if isinstance(images, str):
            images = json.loads(images)
        assert images and len(images) >= 1


# ── Fixture mock_storage (reutilizada del conftest no global) ─────────────────

@pytest.fixture()
def mock_storage(tmp_path):
    from unittest.mock import patch
    import app.services.storage_service as svc

    def fake_save(content: bytes, ext: str, machine_id: int) -> str:
        import uuid
        folder = tmp_path / str(machine_id)
        folder.mkdir(parents=True, exist_ok=True)
        fname = f"{uuid.uuid4().hex}.{ext}"
        (folder / fname).write_bytes(content)
        return f"/static/uploads/machines/{machine_id}/{fname}"

    def fake_delete(url: str) -> None:
        if not url.startswith("/static/uploads/machines/"):
            return
        parts = url.removeprefix("/static/uploads/machines/").split("/", 1)
        if len(parts) == 2:
            path = tmp_path / parts[0] / parts[1]
            try:
                path.unlink()
            except FileNotFoundError:
                pass

    with patch.object(svc, "save_file", side_effect=fake_save), \
         patch.object(svc, "delete_file", side_effect=fake_delete):
        yield
