import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import jwt
import pytest
from argon2 import PasswordHasher
from fastapi import HTTPException, Response

from conftest import TEST_SECRET


def finish(coroutine):
    """These routes perform synchronous DB operations and never yield to I/O."""
    try:
        coroutine.send(None)
    except StopIteration as completed:
        return completed.value
    finally:
        coroutine.close()
    raise AssertionError("Route unexpectedly required an event loop")


@pytest.fixture
def auth(auth_module, monkeypatch):
    connection = MagicMock()
    monkeypatch.setattr(auth_module, "connection", connection)
    monkeypatch.setattr(auth_module, "cursor", connection.cursor.return_value)
    monkeypatch.setattr(auth_module, "secret_key", TEST_SECRET)
    monkeypatch.setattr(auth_module, "algorithm", "HS256")
    connection.cursor.return_value.fetchone.return_value = None
    connection.cursor.return_value.fetchall.return_value = []
    return SimpleNamespace(module=auth_module, db=connection, cursor=connection.cursor.return_value)


def row(auth, token):
    return (17, 3, auth.module.refresh_fingerprint(token), datetime.date.today() + datetime.timedelta(days=10), False)


def test_login_only_hashes_password_and_returns_safe_profile(auth, monkeypatch):
    auth.cursor.fetchone.return_value = (3, "teste", "password-hash", "Nome", datetime.date.today())
    hasher = MagicMock()
    monkeypatch.setattr(auth.module, "pswdHasher", hasher)
    response = Response()
    result = finish(auth.module.login(auth.module.Login(login="teste", password="SenhaValida123"), response))
    assert result["user"] == {"id": 3, "login": "teste", "username": "Nome", "content": []}
    hasher.verify.assert_called_once_with("password-hash", "SenhaValida123")
    hasher.hash.assert_not_called()
    assert auth.cursor.execute.call_args.args[1][1].startswith("sha256:")
    assert "password-hash" not in str(result)


def test_logout_fast_path_skips_all_password_hash_checks(auth, monkeypatch):
    token = auth.module.create_refresh_token(3)
    auth.cursor.fetchone.return_value = row(auth, token)
    hasher = MagicMock()
    monkeypatch.setattr(auth.module, "pswdHasher", hasher)
    response = Response()
    finish(auth.module.logout(response, SimpleNamespace(cookies={"refresh_token": token})))
    assert auth.cursor.execute.call_count == 2
    assert auth.cursor.execute.call_args_list[0].args[1] == (3, auth.module.refresh_fingerprint(token))
    assert auth.cursor.execute.call_args.args[1] == (17,)
    auth.cursor.fetchall.assert_not_called()
    hasher.verify.assert_not_called()
    auth.db.commit.assert_called_once()
    assert sum(b"Max-Age=0" in value for key, value in response.raw_headers if key == b"set-cookie") == 2


@pytest.mark.parametrize("token", [None, "broken", jwt.encode({"sub": "3", "type": "refresh"}, TEST_SECRET, algorithm="HS256")])
def test_logout_missing_or_invalid_token_does_not_query_database(auth, token):
    finish(auth.module.logout(Response(), SimpleNamespace(cookies={"refresh_token": token})))
    auth.cursor.execute.assert_not_called()
    auth.db.commit.assert_not_called()


def test_legacy_session_lookup_is_scoped_to_signed_owner(auth):
    token = auth.module.create_refresh_token(3)
    legacy = (17, 3, PasswordHasher().hash(token), datetime.date.today() + datetime.timedelta(days=1), False)
    auth.cursor.fetchall.return_value = [legacy]
    assert auth.module.find_refresh_session(token) == legacy
    query, params = auth.cursor.execute.call_args.args
    assert "user_id = %s" in query and "expires_at >= CURRENT_DATE" in query
    assert params == (3, "$argon2%")


def test_refresh_fast_path_rotates_without_argon2(auth, monkeypatch):
    token = auth.module.create_refresh_token(3)
    auth.cursor.fetchone.return_value = row(auth, token)
    hasher = MagicMock()
    monkeypatch.setattr(auth.module, "pswdHasher", hasher)
    result = finish(auth.module.refresh(Response(), SimpleNamespace(cookies={"refresh_token": token})))
    assert result["message"] == "Access token renovado"
    assert auth.cursor.execute.call_count == 3
    assert auth.cursor.execute.call_args.args[1][1].startswith("sha256:")
    hasher.verify.assert_not_called()
    hasher.hash.assert_not_called()


def test_rotation_race_cannot_issue_new_tokens(auth):
    token = auth.module.create_refresh_token(3)
    auth.cursor.fetchone.return_value = row(auth, token)
    auth.cursor.rowcount = 0
    response = Response()
    with pytest.raises(HTTPException) as failure:
        finish(auth.module.refresh(response, SimpleNamespace(cookies={"refresh_token": token})))
    assert failure.value.status_code == 401
    assert auth.cursor.execute.call_count == 2
    auth.db.commit.assert_not_called()
    auth.db.rollback.assert_called_once()
    assert "set-cookie" not in response.headers


def test_expired_jwt_rejected_before_database(auth):
    token = jwt.encode({"sub": "3", "type": "refresh", "exp": 1}, TEST_SECRET, algorithm="HS256")
    assert auth.module.find_refresh_session(token) is None
    auth.cursor.execute.assert_not_called()


def test_access_token_cannot_be_used_as_refresh(auth):
    assert auth.module.find_refresh_session(auth.module.create_access_token(3)) is None
    auth.cursor.execute.assert_not_called()


def test_revoked_session_rejected(auth):
    token = auth.module.create_refresh_token(3)
    with pytest.raises(HTTPException) as failure:
        finish(auth.module.refresh(Response(), SimpleNamespace(cookies={"refresh_token": token})))
    assert failure.value.status_code == 401
    auth.db.commit.assert_not_called()
    assert all("revoked = false" in call.args[0] for call in auth.cursor.execute.call_args_list)

