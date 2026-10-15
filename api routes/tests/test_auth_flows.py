import datetime
from unittest.mock import patch

import jwt
import psycopg2
import pytest
from argon2 import PasswordHasher


DATA = {"email": "user@example.com", "password": "SenhaValida123!", "name": "Teste"}


@pytest.mark.parametrize("missing", ["email", "password", "name"])
def test_register_required_fields(api, missing):
    data = {k: v for k, v in DATA.items() if k != missing}
    assert api.client.post("/register", json=data).status_code == 422
    api.db.auth.cursor.return_value.execute.assert_not_called()


def test_register_password_too_long(api):
    assert api.client.post("/register", json={**DATA, "password": "a" * 65}).status_code == 422
    api.db.auth.commit.assert_not_called()


def test_register_duplicate_email_returns_conflict(api):
    api.db.auth.cursor.return_value.execute.side_effect = psycopg2.errors.UniqueViolation("duplicate test email")
    assert api.client.post("/register", json=DATA).status_code == 409
    api.db.auth.rollback.assert_called_once()
    api.db.auth.commit.assert_not_called()


def test_register_database_failure_rolls_back(api):
    api.db.auth.cursor.return_value.execute.side_effect = psycopg2.OperationalError("test database unavailable")
    response = api.client.post("/register", json=DATA)
    assert response.status_code in (500, 503)
    api.db.auth.rollback.assert_called_once()
    api.db.auth.commit.assert_not_called()


@pytest.fixture
def existing_user(api):
    hashed = PasswordHasher().hash(DATA["password"])
    api.db.auth.cursor.return_value.fetchone.return_value = (1, DATA["email"], hashed, "Teste", datetime.date.today())
    return api


def test_login_success_tokens_and_secure_cookies(existing_user):
    api = existing_user
    response = api.client.post("/login", json=DATA)
    assert response.status_code == 200
    assert response.json()["status"] == "sucesso"
    for name, token_type, max_age in [("access_token", "access", 900), ("refresh_token", "refresh", 2592000)]:
        token = response.cookies[name]
        payload = jwt.decode(token, api.modules.auth.secret_key, algorithms=["HS256"])
        assert payload["sub"] == "1"
        assert payload["type"] == token_type
        remaining = payload["exp"] - datetime.datetime.now(datetime.timezone.utc).timestamp()
        assert max_age - 10 < remaining <= max_age
        cookie = next(h.lower() for h in response.headers.get_list("set-cookie") if h.startswith(name + "="))
        assert all(flag in cookie for flag in ["httponly", "secure", "samesite=lax", f"max-age={max_age}"])
    params = api.db.auth.cursor.return_value.execute.call_args.args[1]
    assert params[0] == 1
    assert PasswordHasher().verify(params[1], response.cookies["refresh_token"])
    api.db.auth.commit.assert_called_once()


@pytest.mark.parametrize("known_user", [True, False])
def test_login_invalid_credentials(api, known_user):
    api.db.auth.cursor.return_value.fetchone.return_value = (
        (1, DATA["email"], PasswordHasher().hash("OutraSenha123!"), "Teste", datetime.date.today())
        if known_user else None
    )
    response = api.client.post("/login", json=DATA)
    assert response.status_code == 401
    assert response.json()["detail"] == "E-mail ou senha incorretos."
    assert "set-cookie" not in response.headers
    api.db.auth.commit.assert_not_called()


@pytest.mark.parametrize("data", [{}, {"email": "invalido", "password": "12345678"}, {"email": "a@example.com", "password": "1"}])
def test_login_invalid_input(api, data):
    assert api.client.post("/login", json=data).status_code == 422


def test_logout_revokes_matching_token_and_removes_cookies(api):
    token = "test-refresh-cookie"
    api.client.cookies.set("refresh_token", token)
    api.db.auth.cursor.return_value.fetchall.return_value = [
        (10, PasswordHasher().hash("different-token")), (11, "bad-hash"),
        (12, PasswordHasher().hash(token)),
    ]
    response = api.client.post("/logout")
    assert response.status_code == 200
    updates = [c.args for c in api.db.auth.cursor.return_value.execute.call_args_list if "UPDATE" in c.args[0]]
    assert len(updates) == 1 and updates[0][1] == (12,)
    api.db.auth.commit.assert_called_once()
    cookies = response.headers.get_list("set-cookie")
    for name in ("access_token", "refresh_token"):
        assert any(h.startswith(name + "=") and "Max-Age=0" in h for h in cookies)


def test_logout_without_cookie(api):
    api.db.auth.cursor.return_value.fetchall.return_value = []
    assert api.client.post("/logout").status_code == 200
    api.db.auth.commit.assert_not_called()


@pytest.mark.parametrize("scenario", ["missing", "invalid", "expired", "revoked"])
def test_refresh_rejects_invalid_session(api, scenario):
    token = "refresh-test"
    if scenario != "missing":
        api.client.cookies.set("refresh_token", token)
    rows = []
    if scenario in ("invalid", "expired"):
        hash_value = PasswordHasher().hash(token if scenario == "expired" else "other")
        rows = [(1, 1, hash_value, datetime.date.today() - datetime.timedelta(days=1), False)]
    api.db.auth.cursor.return_value.fetchall.return_value = rows
    assert api.client.post("/refresh").status_code == 401
    api.db.auth.commit.assert_not_called()


def test_refresh_valid_rotates_token(api):
    api.client.cookies.set("refresh_token", "old-refresh")
    api.db.auth.cursor.return_value.fetchall.return_value = [(3, 1, PasswordHasher().hash("old-refresh"), datetime.date.today() + datetime.timedelta(days=10), False)]
    response = api.client.post("/refresh")
    assert response.status_code == 200
    calls = api.db.auth.cursor.return_value.execute.call_args_list
    assert calls[1].args[1] == (3,)
    assert "UPDATE refreshtoken SET revoked=true" in calls[1].args[0]
    assert PasswordHasher().verify(calls[2].args[1][1], response.cookies["refresh_token"])
    api.db.auth.commit.assert_called_once()


def test_refresh_tokens_are_unique_even_in_same_second(api):
    # Congela o relogio para reproduzir duas emissoes no mesmo segundo.
    fixed = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
    with patch.object(api.modules.auth.datetime, "datetime") as clock:
        clock.now.return_value = fixed
        first = api.modules.auth.create_refresh_token(1)
        second = api.modules.auth.create_refresh_token(1)
    assert first != second, "Refresh precisa de identificador unico para impedir replay apos rotacao"
