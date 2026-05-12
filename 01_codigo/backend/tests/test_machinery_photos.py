"""
Tests de subida y eliminación de fotos de maquinaria.

Cubre:
- Subir 1 foto (JPEG) → 200, imagen en la respuesta
- Subir varias fotos (PNG, WebP) → 200
- Superar límite de 10 fotos → 422
- Tipo de archivo no permitido → 422
- Archivo demasiado grande (>5 MB) → 422
- Eliminar fotos → 200, lista actualizada
- Primera foto es la portada (posición 0 en images)
- Sin autenticación → 401
- Propietario incorrecto → 403
- Máquina no encontrada → 404
"""
import io
import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# ── Bytes mínimos que pasan la validación de magic bytes ─────────────────────

def make_jpeg(size: int = 512) -> bytes:
    """Devuelve bytes con cabecera JPEG válida."""
    header = b'\xff\xd8\xff\xe0' + b'\x00' * 12
    return header + b'\x00' * max(0, size - len(header))


def make_png(size: int = 512) -> bytes:
    """Devuelve bytes con cabecera PNG válida."""
    header = b'\x89PNG\r\n\x1a\n' + b'\x00' * 4
    return header + b'\x00' * max(0, size - len(header))


def make_webp(size: int = 512) -> bytes:
    """Devuelve bytes con cabecera WebP válida (RIFF....WEBP)."""
    header = b'RIFF' + b'\x00\x00\x00\x00' + b'WEBP' + b'\x00' * 4
    return header + b'\x00' * max(0, size - len(header))


def make_invalid() -> bytes:
    """Bytes que no corresponden a ningún tipo permitido."""
    return b'\x00\x01\x02\x03' + b'\x00' * 100


# ── Fixtures ──────────────────────────────────────────────────────────────────

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
MACHINERY_URL = "/api/v1/machinery"

PUBLISHER_DATA = {
    "email": "photo_publisher@test.com",
    "username": "photo_publisher",
    "password": "Segura123",
    "role": "publisher",
}

OTHER_PUBLISHER_DATA = {
    "email": "other_photo@test.com",
    "username": "other_photo",
    "password": "Segura123",
    "role": "publisher",
}

MACHINERY_DATA = {
    "title": "Excavadora de prueba fotos",
    "description": "Descripción de prueba con más de veinte caracteres aquí",
    "machinery_type": "excavadora",
    "daily_rate": 150.0,
    "location_city": "Madrid",
    "location_province": "Madrid",
}


def _register_and_login(client, user_data: dict) -> str:
    """Registra un usuario y devuelve el access_token."""
    client.post(REGISTER_URL, json=user_data)
    resp = client.post(LOGIN_URL, json={
        "email": user_data["email"],
        "password": user_data["password"],
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    return resp.json()["access_token"]


def _create_machinery(client, token: str) -> dict:
    """Crea una máquina y devuelve el JSON de respuesta."""
    resp = client.post(
        MACHINERY_URL,
        json=MACHINERY_DATA,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201, f"Create failed: {resp.text}"
    return resp.json()


def _upload_url(machine_id: int) -> str:
    return f"/api/v1/machinery/{machine_id}/photos"


def _delete_url(machine_id: int) -> str:
    return f"/api/v1/machinery/{machine_id}/photos"


def _file_tuple(content: bytes, filename: str = "photo.jpg", ctype: str = "image/jpeg"):
    """Devuelve la tupla que acepta httpx para multipart."""
    return (filename, io.BytesIO(content), ctype)


# ── Parche global del storage para no escribir en disco ───────────────────────

@pytest.fixture(autouse=True)
def mock_storage(tmp_path):
    """
    Redirige UPLOAD_BASE al directorio temporal de pytest y
    reemplaza save_file / delete_file con versiones que usan tmp_path.
    """
    import app.services.storage_service as svc

    real_upload_base = svc.UPLOAD_BASE

    def fake_save(content: bytes, ext: str, machine_id: int) -> str:
        folder = tmp_path / str(machine_id)
        folder.mkdir(parents=True, exist_ok=True)
        import uuid
        filename = f"{uuid.uuid4().hex}.{ext}"
        (folder / filename).write_bytes(content)
        return f"/static/uploads/machines/{machine_id}/{filename}"

    def fake_delete(url: str) -> None:
        if not url.startswith("/static/uploads/machines/"):
            return
        relative = url.removeprefix("/static/uploads/machines/")
        parts = relative.split("/", 1)
        if len(parts) == 2:
            machine_id, filename = parts
            path = tmp_path / machine_id / filename
            try:
                path.unlink()
            except FileNotFoundError:
                pass

    with patch.object(svc, "save_file", side_effect=fake_save), \
         patch.object(svc, "delete_file", side_effect=fake_delete):
        yield


# ── Tests: autenticación y permisos ──────────────────────────────────────────

class TestPhotoPermissions:

    def test_upload_without_auth_returns_401(self, client):
        resp = client.post(
            _upload_url(999),
            files={"files": _file_tuple(make_jpeg())},
        )
        assert resp.status_code == 401

    def test_delete_without_auth_returns_401(self, client):
        resp = client.request(
            "DELETE",
            _delete_url(999),
            json={"urls": ["/static/uploads/machines/999/abc.jpg"]},
        )
        assert resp.status_code == 401

    def test_upload_wrong_owner_returns_403(self, client):
        token_a = _register_and_login(client, PUBLISHER_DATA)
        token_b = _register_and_login(client, OTHER_PUBLISHER_DATA)
        machine = _create_machinery(client, token_a)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert resp.status_code == 403

    def test_upload_nonexistent_machine_returns_404(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        resp = client.post(
            _upload_url(99999),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 404


# ── Tests: subida correcta ────────────────────────────────────────────────────

class TestPhotoUpload:

    def test_upload_one_jpeg_returns_200(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg(), "foto1.jpg", "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_upload_one_jpeg_images_list_has_one_url(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token}"},
        )
        data = resp.json()
        assert isinstance(data["images"], list)
        assert len(data["images"]) == 1

    def test_upload_one_jpeg_url_starts_with_static(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token}"},
        )
        url = resp.json()["images"][0]
        assert url.startswith("/static/uploads/machines/")

    def test_upload_png_is_accepted(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_png(), "foto.png", "image/png")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_upload_webp_is_accepted(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_webp(), "foto.webp", "image/webp")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_upload_multiple_photos_appends_all(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "a.jpg")),
                ("files", _file_tuple(make_png(), "b.png", "image/png")),
                ("files", _file_tuple(make_webp(), "c.webp", "image/webp")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["images"]) == 3

    def test_upload_appends_to_existing_photos(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        # Primera subida: 2 fotos
        client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "a.jpg")),
                ("files", _file_tuple(make_jpeg(), "b.jpg")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )

        # Segunda subida: 3 fotos más
        resp = client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_png(), "c.png", "image/png")),
                ("files", _file_tuple(make_png(), "d.png", "image/png")),
                ("files", _file_tuple(make_png(), "e.png", "image/png")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["images"]) == 5

    def test_first_uploaded_photo_is_cover(self, client):
        """La primera foto (índice 0) es la portada."""
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "primero.jpg")),
                ("files", _file_tuple(make_png(), "segundo.png", "image/png")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )
        images = resp.json()["images"]
        assert images[0].endswith(".jpg")

    def test_upload_exactly_10_photos_is_accepted(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        files = [("files", _file_tuple(make_jpeg(), f"f{i}.jpg")) for i in range(10)]
        resp = client.post(
            _upload_url(machine["id"]),
            files=files,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["images"]) == 10


# ── Tests: validación ─────────────────────────────────────────────────────────

class TestPhotoValidation:

    def test_invalid_mime_type_returns_422(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_invalid(), "virus.exe", "application/octet-stream")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_file_too_large_returns_422(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        big_file = make_jpeg(size=6 * 1024 * 1024)  # 6 MB > límite 5 MB
        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(big_file, "grande.jpg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_exceeding_10_photo_limit_returns_422(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        # Subir 10 fotos primero
        files_10 = [("files", _file_tuple(make_jpeg(), f"f{i}.jpg")) for i in range(10)]
        client.post(
            _upload_url(machine["id"]),
            files=files_10,
            headers={"Authorization": f"Bearer {token}"},
        )

        # Intentar añadir 1 más (total sería 11)
        resp = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg(), "once.jpg")},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_exceeding_limit_in_single_request_returns_422(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        files_11 = [("files", _file_tuple(make_jpeg(), f"f{i}.jpg")) for i in range(11)]
        resp = client.post(
            _upload_url(machine["id"]),
            files=files_11,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422

    def test_zero_files_returns_422(self, client):
        """Enviar la petición sin ningún fichero → error de validación."""
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.post(
            _upload_url(machine["id"]),
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 422


# ── Tests: eliminación ────────────────────────────────────────────────────────

class TestPhotoDelete:

    def test_delete_photo_returns_200(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        up = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token}"},
        )
        url = up.json()["images"][0]

        resp = client.request(
            "DELETE",
            _delete_url(machine["id"]),
            json={"urls": [url]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_delete_photo_removes_from_images_list(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        up = client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "a.jpg")),
                ("files", _file_tuple(make_jpeg(), "b.jpg")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )
        images = up.json()["images"]
        url_to_delete = images[0]

        resp = client.request(
            "DELETE",
            _delete_url(machine["id"]),
            json={"urls": [url_to_delete]},
            headers={"Authorization": f"Bearer {token}"},
        )
        remaining = resp.json()["images"]
        assert len(remaining) == 1
        assert url_to_delete not in remaining

    def test_delete_all_photos_leaves_empty_list(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        up = client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "a.jpg")),
                ("files", _file_tuple(make_jpeg(), "b.jpg")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )
        images = up.json()["images"]

        resp = client.request(
            "DELETE",
            _delete_url(machine["id"]),
            json={"urls": images},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.json()["images"] == []

    def test_delete_nonexistent_url_is_idempotent(self, client):
        """Eliminar una URL que no existe no debe dar error."""
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        resp = client.request(
            "DELETE",
            _delete_url(machine["id"]),
            json={"urls": ["/static/uploads/machines/999/no_existe.jpg"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200

    def test_delete_wrong_owner_returns_403(self, client):
        token_a = _register_and_login(client, PUBLISHER_DATA)
        token_b = _register_and_login(client, OTHER_PUBLISHER_DATA)
        machine = _create_machinery(client, token_a)

        up = client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token_a}"},
        )
        url = up.json()["images"][0]

        resp = client.request(
            "DELETE",
            _delete_url(machine["id"]),
            json={"urls": [url]},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert resp.status_code == 403


# ── Tests: visualización ──────────────────────────────────────────────────────

class TestPhotoDisplay:

    def test_get_machinery_includes_images_list(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get(f"/api/v1/machinery/{machine['id']}")
        assert resp.status_code == 200
        data = resp.json()
        assert "images" in data
        assert len(data["images"]) == 1

    def test_search_machinery_includes_images(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "a.jpg")),
                ("files", _file_tuple(make_png(), "b.png", "image/png")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get("/api/v1/machinery/search")
        assert resp.status_code == 200
        machinery_list = resp.json()["machinery"]
        found = next((m for m in machinery_list if m["id"] == machine["id"]), None)
        assert found is not None
        assert len(found["images"]) == 2

    def test_my_machinery_includes_images(self, client):
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        client.post(
            _upload_url(machine["id"]),
            files={"files": _file_tuple(make_jpeg())},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get(
            "/api/v1/machinery/my/machinery",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        found = next((m for m in resp.json() if m["id"] == machine["id"]), None)
        assert found is not None
        assert len(found["images"]) == 1

    def test_cover_is_first_image_in_list(self, client):
        """El campo images[0] siempre es la imagen de portada."""
        token = _register_and_login(client, PUBLISHER_DATA)
        machine = _create_machinery(client, token)

        client.post(
            _upload_url(machine["id"]),
            files=[
                ("files", _file_tuple(make_jpeg(), "portada.jpg")),
                ("files", _file_tuple(make_png(), "segunda.png", "image/png")),
                ("files", _file_tuple(make_webp(), "tercera.webp", "image/webp")),
            ],
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get(f"/api/v1/machinery/{machine['id']}")
        images = resp.json()["images"]
        assert len(images) == 3
        # La portada es la primera (jpg)
        assert images[0].endswith(".jpg")
