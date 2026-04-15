"""
Tests de internacionalización — Cambio B (backend)
===================================================
B1 – El campo preferred_language existe en la tabla users y tiene default 'es'.
B2 – GET /users/me devuelve preferred_language en la respuesta.
B3 – PATCH /users/me/language acepta 'es', 'ca', 'en' y guarda el valor.
B4 – PATCH /users/me/language con idioma inválido → 422.
B5 – PATCH /users/me/language sin autenticación → 401.
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL    = "/api/v1/auth/login"
ME_URL       = "/api/v1/users/me"
LANG_URL     = "/api/v1/users/me/language"

USER_DATA = {
    "email": "i18n_user@test.com",
    "username": "i18n_user",
    "password": "Segura123",
    "role": "consumer",
}


def _register_and_login(client):
    client.post(REGISTER_URL, json=USER_DATA)
    resp = client.post(LOGIN_URL, json={
        "email": USER_DATA["email"],
        "password": USER_DATA["password"],
    })
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────

class TestPreferredLanguageField:

    def test_B1_default_language_is_es(self, client, db):
        """B1 – nuevo usuario tiene preferred_language='es' por defecto"""
        client.post(REGISTER_URL, json=USER_DATA)
        from app.models.user import User
        user = db.query(User).filter(User.email == USER_DATA["email"]).first()
        assert user is not None
        assert user.preferred_language == "es"

    def test_B2_me_response_includes_preferred_language(self, client):
        """B2 – GET /users/me incluye el campo preferred_language"""
        headers = _register_and_login(client)
        resp = client.get(ME_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "preferred_language" in data
        assert data["preferred_language"] == "es"


class TestPatchLanguage:

    def test_B3_patch_language_es(self, client):
        """B3 – PATCH /users/me/language actualiza a 'es'"""
        headers = _register_and_login(client)
        resp = client.patch(LANG_URL, json={"language": "es"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["preferred_language"] == "es"

    def test_B3_patch_language_ca(self, client):
        """B3 – PATCH /users/me/language actualiza a 'ca'"""
        headers = _register_and_login(client)
        resp = client.patch(LANG_URL, json={"language": "ca"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["preferred_language"] == "ca"

    def test_B3_patch_language_en(self, client):
        """B3 – PATCH /users/me/language actualiza a 'en'"""
        headers = _register_and_login(client)
        resp = client.patch(LANG_URL, json={"language": "en"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["preferred_language"] == "en"

    def test_B3_patch_language_persisted(self, client, db):
        """B3 – El cambio de idioma se persiste en la base de datos"""
        headers = _register_and_login(client)
        client.patch(LANG_URL, json={"language": "ca"}, headers=headers)
        from app.models.user import User
        user = db.query(User).filter(User.email == USER_DATA["email"]).first()
        assert user.preferred_language == "ca"

    def test_B4_invalid_language_returns_422(self, client):
        """B4 – PATCH con idioma desconocido devuelve 422"""
        headers = _register_and_login(client)
        resp = client.patch(LANG_URL, json={"language": "fr"}, headers=headers)
        assert resp.status_code == 422

    def test_B5_unauthenticated_returns_401(self, client):
        """B5 – Sin token → 401"""
        resp = client.patch(LANG_URL, json={"language": "en"})
        assert resp.status_code == 401
