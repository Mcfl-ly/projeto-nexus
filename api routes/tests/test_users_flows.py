import datetime

import pytest
from argon2 import PasswordHasher


@pytest.mark.parametrize("route", ["/users/me", "/library"])
@pytest.mark.parametrize("case", ["missing", "invalid", "expired", "refresh", "empty_sub"])
def test_protected_routes_reject_bad_tokens(api, access_token, route, case):
    tokens = {
        "invalid": "broken-token", "expired": access_token(exp=1),
        "refresh": access_token(type="refresh"), "empty_sub": access_token(sub=""),
    }
    if case != "missing":
        api.client.cookies.set("access_token", tokens[case])
    assert api.client.get(route).status_code == 401
    api.db.users.cursor.return_value.execute.assert_not_called()
    api.db.library.cursor.return_value.execute.assert_not_called()


@pytest.mark.parametrize("method,route,body", [
    ("patch", "/users/me", {"username": "Novo"}),
    ("patch", "/users/me/password", {"password": "SenhaNova123"}),
    ("delete", "/users/me/delete", None),
    ("post", "/library", {"title": "Teste", "type": "book"}),
    ("post", "/library/manual", {"title": "Teste", "type": "book"}),
    ("patch", "/library/1", {"rating": 5}), ("delete", "/library/1", None),
])
def test_mutations_require_authentication(api, method, route, body):
    assert api.client.request(method, route, json=body).status_code == 401


def test_profile_returns_user_without_password(logged_api):
    api = logged_api
    api.db.users.cursor.return_value.fetchone.return_value = (1, "a@example.com", "private-hash", "Alice", datetime.date(2026, 1, 1))
    api.db.users.cursor.return_value.fetchall.return_value = []
    response = api.client.get("/users/me")
    assert response.status_code == 200
    assert response.json() == {"email": "a@example.com", "username": "Alice", "created_at": "2026-01-01", "content": []}
    assert "private-hash" not in response.text
    assert all(call.args[1] == ("1",) for call in api.db.users.cursor.return_value.execute.call_args_list)


def test_profile_missing_user_is_not_server_error(logged_api):
    logged_api.db.users.cursor.return_value.fetchone.return_value = None
    logged_api.db.users.cursor.return_value.fetchall.return_value = []
    assert logged_api.client.get("/users/me").status_code in (401, 404)


def test_profile_content_type_uses_content_type_column(logged_api):
    api = logged_api
    api.db.users.cursor.return_value.fetchone.return_value = (1, "a@example.com", "hash", "Alice", datetime.date.today())
    api.db.users.cursor.return_value.fetchall.return_value = [(1, 1, "mongo-id", "Duna", "Quero Ler", None, datetime.date.today(), "OL123", "book")]
    response = api.client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["content"][0]["type"] == "book"


def test_update_username_uses_current_user(logged_api):
    api = logged_api
    api.db.users.cursor.return_value.fetchone.return_value = ("Alice",)
    response = api.client.patch("/users/me", json={"username": "Novo", "user_id": 999})
    assert response.status_code == 200
    assert response.json() == {"name": "Novo"}
    assert api.db.users.cursor.return_value.execute.call_args.args[1] == ("Novo", 1)
    api.db.users.commit.assert_called_once()


def test_update_missing_user(logged_api):
    logged_api.db.users.cursor.return_value.fetchone.return_value = None
    assert logged_api.client.patch("/users/me", json={"username": "Novo"}).status_code == 404
    logged_api.db.users.commit.assert_not_called()


@pytest.mark.parametrize("data", [{}, {"username": None}])
def test_update_username_does_not_write_null(logged_api, data):
    logged_api.db.users.cursor.return_value.fetchone.return_value = ("Alice",)
    assert logged_api.client.patch("/users/me", json=data).status_code == 422
    logged_api.db.users.commit.assert_not_called()


def test_password_update_hashes_and_targets_current_user(logged_api):
    api = logged_api
    response = api.client.patch("/users/me/password", json={"password": "NovaSenha123!", "user_id": 999})
    assert response.status_code == 200
    hashed, user_id = api.db.users.cursor.return_value.execute.call_args.args[1]
    assert user_id == 1
    assert PasswordHasher().verify(hashed, "NovaSenha123!")
    api.db.users.commit.assert_called_once()


@pytest.mark.parametrize("password", ["a", "a" * 65])
def test_password_update_validation(logged_api, password):
    assert logged_api.client.patch("/users/me/password", json={"password": password}).status_code == 422
    logged_api.db.users.commit.assert_not_called()


def test_delete_account_removes_children_before_user(logged_api):
    api = logged_api
    assert api.client.delete("/users/me/delete").status_code == 200
    calls = api.db.users.cursor.return_value.execute.call_args_list
    assert len(calls) == 3
    assert [c.args[0].split()[2] for c in calls] == ["refreshtoken", "userlibrary", "users"]
    assert all(c.args[1] == (1,) for c in calls)
    api.db.users.commit.assert_called_once()
