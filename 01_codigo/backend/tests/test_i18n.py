"""
Tests de internacionalización — Cambio B (backend)
===================================================
B1 – Campo preferred_language existe con default 'es'.
B2 – GET /users/me devuelve preferred_language.
B3 – PATCH /users/me/language acepta es/ca/en y persiste.
B4 – Persistencia entre sesiones (logout → login → idioma conservado).
B5 – Aislamiento entre usuarios (cambio de A no afecta a B).
"""
import pytest

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL    = "/api/v1/auth/login"
ME_URL       = "/api/v1/users/me"
LANG_URL     = "/api/v1/users/me/language"

USER_A = {
    "email":    "user_a_i18n@test.com",
    "username": "user_a_i18n",
    "password": "Segura123",
    "role":     "consumer",
}
USER_B = {
    "email":    "user_b_i18n@test.com",
    "username": "user_b_i18n",
    "password": "Segura123",
    "role":     "consumer",
}


def _register_and_login(client, user_data):
    client.post(REGISTER_URL, json=user_data)
    resp = client.post(LOGIN_URL, json={
        "email":    user_data["email"],
        "password": user_data["password"],
    })
    assert resp.status_code == 200, f"Login falló: {resp.text}"
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# B1 / B2
# ─────────────────────────────────────────────────────────────────────────────

class TestPreferredLanguageField:

    def test_B1_default_language_is_es(self, client, db):
        """B1 – nuevo usuario tiene preferred_language='es' por defecto"""
        client.post(REGISTER_URL, json=USER_A)
        from app.models.user import User
        user = db.query(User).filter(User.email == USER_A["email"]).first()
        assert user is not None
        assert user.preferred_language == "es"

    def test_B2_me_response_includes_preferred_language(self, client):
        """B2 – GET /users/me incluye el campo preferred_language con valor 'es'"""
        headers = _register_and_login(client, USER_A)
        resp = client.get(ME_URL, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "preferred_language" in data
        assert data["preferred_language"] == "es"


# ─────────────────────────────────────────────────────────────────────────────
# B3 – PATCH /users/me/language
# ─────────────────────────────────────────────────────────────────────────────

class TestPatchLanguage:

    def test_B3_patch_language_es(self, client):
        """B3 – PATCH a 'es' → 200 y respuesta con preferred_language='es'"""
        headers = _register_and_login(client, USER_A)
        resp = client.patch(LANG_URL, json={"language": "es"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["preferred_language"] == "es"

    def test_B3_patch_language_ca(self, client):
        """B3 – PATCH a 'ca' → 200 y respuesta con preferred_language='ca'"""
        headers = _register_and_login(client, USER_A)
        resp = client.patch(LANG_URL, json={"language": "ca"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["preferred_language"] == "ca"

    def test_B3_patch_language_en(self, client):
        """B3 – PATCH a 'en' → 200 y respuesta con preferred_language='en'"""
        headers = _register_and_login(client, USER_A)
        resp = client.patch(LANG_URL, json={"language": "en"}, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["preferred_language"] == "en"

    def test_B3_patch_persists_in_db(self, client, db):
        """B3 – El cambio de idioma se persiste en la base de datos"""
        headers = _register_and_login(client, USER_A)
        client.patch(LANG_URL, json={"language": "ca"}, headers=headers)
        from app.models.user import User
        user = db.query(User).filter(User.email == USER_A["email"]).first()
        assert user.preferred_language == "ca"

    def test_B3_invalid_language_fr_returns_422(self, client):
        """B3 – PATCH con idioma inválido 'fr' → 422"""
        headers = _register_and_login(client, USER_A)
        resp = client.patch(LANG_URL, json={"language": "fr"}, headers=headers)
        assert resp.status_code == 422

    def test_B3_empty_language_returns_422(self, client):
        """B3 – PATCH con idioma vacío '' → 422"""
        headers = _register_and_login(client, USER_A)
        resp = client.patch(LANG_URL, json={"language": ""}, headers=headers)
        assert resp.status_code == 422

    def test_B3_unauthenticated_returns_401(self, client):
        """B3 – Sin token → 401"""
        resp = client.patch(LANG_URL, json={"language": "en"})
        assert resp.status_code == 401


# ─────────────────────────────────────────────────────────────────────────────
# B4 – Persistencia entre sesiones
# ─────────────────────────────────────────────────────────────────────────────

class TestLanguagePersistence:

    def test_B4_language_persists_after_relogin(self, client):
        """
        B4 – El usuario cambia idioma a 'ca', hace logout (descarta el token)
        y vuelve a hacer login. GET /users/me debe devolver 'ca'.
        """
        # 1) Registrar y hacer login
        headers1 = _register_and_login(client, USER_A)
        # 2) Cambiar idioma a 'ca'
        resp = client.patch(LANG_URL, json={"language": "ca"}, headers=headers1)
        assert resp.status_code == 200
        # 3) Simular logout descartando el token y hacer nuevo login
        resp2 = client.post(LOGIN_URL, json={
            "email":    USER_A["email"],
            "password": USER_A["password"],
        })
        assert resp2.status_code == 200
        token2 = resp2.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        # 4) GET /users/me tras re-login → idioma debe ser 'ca'
        resp3 = client.get(ME_URL, headers=headers2)
        assert resp3.status_code == 200
        assert resp3.json()["preferred_language"] == "ca"


# ─────────────────────────────────────────────────────────────────────────────
# B5 – Aislamiento entre usuarios
# ─────────────────────────────────────────────────────────────────────────────

class TestLanguageIsolation:

    def test_B5_changing_a_does_not_affect_b(self, client, db):
        """
        B5 – Usuario A cambia idioma a 'ca', Usuario B cambia a 'en'.
        Verificar en la DB que cada uno conserva su idioma independientemente.
        """
        headers_a = _register_and_login(client, USER_A)
        headers_b = _register_and_login(client, USER_B)

        # A → 'ca'
        r_a = client.patch(LANG_URL, json={"language": "ca"}, headers=headers_a)
        assert r_a.status_code == 200

        # B → 'en'
        r_b = client.patch(LANG_URL, json={"language": "en"}, headers=headers_b)
        assert r_b.status_code == 200

        # Volver a cambiar A → 'es' (no debe tocar a B)
        client.patch(LANG_URL, json={"language": "es"}, headers=headers_a)

        from app.models.user import User
        user_a = db.query(User).filter(User.email == USER_A["email"]).first()
        user_b = db.query(User).filter(User.email == USER_B["email"]).first()

        assert user_a.preferred_language == "es", f"A debería ser 'es', es '{user_a.preferred_language}'"
        assert user_b.preferred_language == "en", f"B debería ser 'en', es '{user_b.preferred_language}'"

    def test_B5_me_endpoint_scoped_to_current_user(self, client):
        """B5 – GET /users/me devuelve datos del usuario autenticado, no del otro."""
        headers_a = _register_and_login(client, USER_A)
        headers_b = _register_and_login(client, USER_B)

        client.patch(LANG_URL, json={"language": "ca"}, headers=headers_a)
        client.patch(LANG_URL, json={"language": "en"}, headers=headers_b)

        resp_a = client.get(ME_URL, headers=headers_a)
        resp_b = client.get(ME_URL, headers=headers_b)

        assert resp_a.json()["preferred_language"] == "ca"
        assert resp_b.json()["preferred_language"] == "en"
