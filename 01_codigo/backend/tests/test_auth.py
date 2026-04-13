"""
Tests del flujo de registro de usuarios — POST /api/v1/auth/register

Cubre:
- Registro válido de consumidor y proveedor (201)
- Usuario persiste en la BD con contraseña hasheada e is_active=True
- Email duplicado → 400
- Contraseña débil (sin número) → 422
- Contraseña débil (sin mayúscula) → 422
- Email inválido → 422
"""
import pytest
from app.models.user import User, UserRole
from app.core.security import verify_password

REGISTER_URL = "/api/v1/auth/register"


# ─────────────────────────────────────────────────────────────────────────────
# Datos de prueba
# ─────────────────────────────────────────────────────────────────────────────

VALID_CONSUMER = {
    "email": "consumer@test.com",
    "username": "consumer_test",
    "password": "Segura123",
    "role": "consumer",
}

VALID_PUBLISHER = {
    "email": "publisher@test.com",
    "username": "publisher_test",
    "password": "Segura123",
    "role": "publisher",
}


# ─────────────────────────────────────────────────────────────────────────────
# Tests de registro válido
# ─────────────────────────────────────────────────────────────────────────────

class TestRegisterSuccess:

    def test_register_consumer_returns_201(self, client):
        response = client.post(REGISTER_URL, json=VALID_CONSUMER)
        assert response.status_code == 201

    def test_register_consumer_response_has_id(self, client):
        response = client.post(REGISTER_URL, json=VALID_CONSUMER)
        data = response.json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_register_consumer_role_is_correct(self, client):
        response = client.post(REGISTER_URL, json=VALID_CONSUMER)
        data = response.json()
        assert data["role"] == "consumer"

    def test_register_consumer_is_active_true(self, client):
        response = client.post(REGISTER_URL, json=VALID_CONSUMER)
        data = response.json()
        assert data["is_active"] is True

    def test_register_consumer_exists_in_db(self, client, db):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        user = db.query(User).filter(User.email == VALID_CONSUMER["email"]).first()
        assert user is not None

    def test_register_consumer_password_is_hashed_in_db(self, client, db):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        user = db.query(User).filter(User.email == VALID_CONSUMER["email"]).first()
        # La contraseña nunca se almacena en texto plano
        assert user.hashed_password != VALID_CONSUMER["password"]

    def test_register_consumer_password_hash_is_valid(self, client, db):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        user = db.query(User).filter(User.email == VALID_CONSUMER["email"]).first()
        # El hash debe verificarse correctamente contra la contraseña original
        assert verify_password(VALID_CONSUMER["password"], user.hashed_password)

    def test_register_publisher_returns_201(self, client):
        response = client.post(REGISTER_URL, json=VALID_PUBLISHER)
        assert response.status_code == 201

    def test_register_publisher_role_is_correct(self, client):
        response = client.post(REGISTER_URL, json=VALID_PUBLISHER)
        data = response.json()
        assert data["role"] == "publisher"

    def test_register_publisher_is_active_true(self, client):
        response = client.post(REGISTER_URL, json=VALID_PUBLISHER)
        data = response.json()
        assert data["is_active"] is True

    def test_register_publisher_exists_in_db(self, client, db):
        client.post(REGISTER_URL, json=VALID_PUBLISHER)
        user = db.query(User).filter(User.email == VALID_PUBLISHER["email"]).first()
        assert user is not None

    def test_register_response_does_not_expose_password(self, client):
        response = client.post(REGISTER_URL, json=VALID_CONSUMER)
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data


# ─────────────────────────────────────────────────────────────────────────────
# Tests de email duplicado
# ─────────────────────────────────────────────────────────────────────────────

class TestRegisterDuplicateEmail:

    def test_duplicate_email_returns_error(self, client):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        response = client.post(REGISTER_URL, json={**VALID_CONSUMER, "username": "otro_user"})
        assert response.status_code in (400, 409, 422)

    def test_duplicate_email_error_message_mentions_email(self, client):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        response = client.post(REGISTER_URL, json={**VALID_CONSUMER, "username": "otro_user"})
        detail = response.json().get("detail", "").lower()
        assert "email" in detail

    def test_duplicate_email_does_not_create_second_user(self, client, db):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        client.post(REGISTER_URL, json={**VALID_CONSUMER, "username": "otro_user"})
        count = db.query(User).filter(User.email == VALID_CONSUMER["email"]).count()
        assert count == 1

    def test_duplicate_username_returns_error(self, client):
        client.post(REGISTER_URL, json=VALID_CONSUMER)
        response = client.post(REGISTER_URL, json={**VALID_CONSUMER, "email": "otro@test.com"})
        assert response.status_code in (400, 409, 422)


# ─────────────────────────────────────────────────────────────────────────────
# Tests de contraseña débil
# ─────────────────────────────────────────────────────────────────────────────

class TestRegisterWeakPassword:

    def test_password_without_number_returns_422(self, client):
        payload = {**VALID_CONSUMER, "password": "SinNumero"}
        response = client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_password_without_uppercase_returns_422(self, client):
        payload = {**VALID_CONSUMER, "password": "sinmayuscula1"}
        response = client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_password_too_short_returns_422(self, client):
        payload = {**VALID_CONSUMER, "password": "Ab1"}
        response = client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_password_without_number_error_mentions_number(self, client):
        payload = {**VALID_CONSUMER, "password": "SinNumero"}
        response = client.post(REGISTER_URL, json=payload)
        detail = str(response.json().get("detail", "")).lower()
        assert "número" in detail or "numero" in detail or "digit" in detail

    def test_password_without_uppercase_error_mentions_uppercase(self, client):
        payload = {**VALID_CONSUMER, "password": "sinmayuscula1"}
        response = client.post(REGISTER_URL, json=payload)
        detail = str(response.json().get("detail", "")).lower()
        assert "mayúscula" in detail or "mayuscula" in detail or "upper" in detail


# ─────────────────────────────────────────────────────────────────────────────
# Tests de email inválido
# ─────────────────────────────────────────────────────────────────────────────

class TestRegisterInvalidEmail:

    def test_missing_at_symbol_returns_422(self, client):
        payload = {**VALID_CONSUMER, "email": "notanemail"}
        response = client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_missing_domain_returns_422(self, client):
        payload = {**VALID_CONSUMER, "email": "user@"}
        response = client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_empty_email_returns_422(self, client):
        payload = {**VALID_CONSUMER, "email": ""}
        response = client.post(REGISTER_URL, json=payload)
        assert response.status_code == 422

    def test_invalid_email_does_not_create_user(self, client, db):
        payload = {**VALID_CONSUMER, "email": "invalidemail"}
        client.post(REGISTER_URL, json=payload)
        count = db.query(User).count()
        assert count == 0
