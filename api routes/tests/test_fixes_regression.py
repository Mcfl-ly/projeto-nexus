import datetime
from pathlib import Path
from unittest.mock import Mock

import psycopg2
import pytest
from argon2 import PasswordHasher
from pymongo.errors import ServerSelectionTimeoutError


@pytest.mark.parametrize("area,method,route,body", [
    ("auth", "post", "/login", {"email": "a@example.com", "password": "ValidPassword123"}),
    ("auth", "post", "/logout", None),
    ("users", "get", "/users/me", None),
    ("users", "patch", "/users/me", {"username": "Novo"}),
    ("users", "patch", "/users/me/password", {"password": "NovaSenha123!"}),
    ("users", "delete", "/users/me/delete", None),
    ("library", "get", "/library", None),
    ("library", "patch", "/library/1", {"rating": 5}),
    ("library", "delete", "/library/1", None),
])
def test_database_errors_are_recoverable(logged_api, area, method, route, body):
    connection = getattr(logged_api.db, area)
    connection.cursor.return_value.execute.side_effect = psycopg2.OperationalError("private database error")
    response = logged_api.client.request(method, route, json=body)
    assert response.status_code == 503
    assert "private database error" not in response.text
    connection.rollback.assert_called_once()
    connection.commit.assert_not_called()


def test_login_commit_error_is_not_invalid_password(api):
    api.db.auth.cursor.return_value.fetchone.return_value = (1, "a@example.com", PasswordHasher().hash("ValidPassword123"), "Nome", datetime.date.today())
    api.db.auth.commit.side_effect = psycopg2.OperationalError("commit failed")
    response = api.client.post("/login", json={"email": "a@example.com", "password": "ValidPassword123"})
    assert response.status_code == 503
    assert "set-cookie" not in response.headers
    api.db.auth.rollback.assert_called_once()


def test_refresh_losing_atomic_update_cannot_issue_session(api):
    api.client.cookies.set("refresh_token", "old-cookie")
    cursor = api.db.auth.cursor.return_value
    cursor.fetchall.return_value = [(3, 1, PasswordHasher().hash("old-cookie"), datetime.date.today() + datetime.timedelta(days=2), False)]
    cursor.rowcount = 0  # Outra transacao ja revogou a sessao.
    response = api.client.post("/refresh")
    assert response.status_code == 401
    statements = [call.args[0] for call in cursor.execute.call_args_list]
    assert "AND revoked = false" in statements[-1]
    assert not any("INSERT" in query for query in statements)
    api.db.auth.commit.assert_not_called()
    api.db.auth.rollback.assert_called_once()
    assert "set-cookie" not in response.headers


@pytest.mark.parametrize("kind", ["game", "movie", "book"])
@pytest.mark.parametrize("malformed", ["invalid_json", "wrong_shape", "missing_id"])
def test_malformed_provider_payload_returns_502(logged_api, monkeypatch, kind, malformed):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = None
    monkeypatch.setattr(api.modules.library, "get_igdb_token", Mock(return_value="fake"))
    if malformed == "invalid_json":
        payload = Mock(side_effect=ValueError("invalid json"))
    else:
        values = {"game": [{}], "movie": {"results": [{}]}, "book": {"docs": [{}]}}
        payload = Mock(return_value="wrong" if malformed == "wrong_shape" else values[kind])
    request = Mock(return_value=Mock(status_code=200, json=payload))
    monkeypatch.setattr(api.modules.library.requests, "post" if kind == "game" else "get", request)
    response = api.client.post("/library", json={"title": "Teste", "type": kind})
    assert response.status_code == 502
    api.db.library.commit.assert_not_called()
    assert request.call_args.kwargs["timeout"] == (3.05, 10)


@pytest.mark.parametrize("kind,payload", [
    ("game", [{"id": 1, "name": "Teste"}]),
    ("book", {"docs": [{"key": "OL1", "title": "Teste"}]}),
    ("movie", {"results": [{"id": 1, "title": "Teste"}]}),
])
def test_provider_optional_fields_can_be_absent(api, monkeypatch, kind, payload):
    monkeypatch.setattr(api.modules.library, "get_igdb_token", Mock(return_value="fake"))
    monkeypatch.setattr(api.modules.library.requests, "post" if kind == "game" else "get", Mock(return_value=Mock(status_code=200, json=Mock(return_value=payload))))
    result = getattr(api.modules.library, f"search_{kind}_in_external_api")("Teste")
    assert result["title"] == "teste" and result["genres"] == []


def test_book_translation_fallback_sends_second_request(api, monkeypatch):
    monkeypatch.setattr(api.modules.library, "translate_title", Mock(return_value="translated"))
    request = Mock(side_effect=[
        Mock(status_code=200, json=Mock(return_value={"docs": []})),
        Mock(status_code=200, json=Mock(return_value={"docs": [{"key": "OL1", "title": "Translated"}]})),
    ])
    monkeypatch.setattr(api.modules.library.requests, "get", request)
    result = api.modules.library.search_book_in_external_api("Titulo")
    assert result["external_id"] == "OL1"
    assert request.call_count == 2
    assert request.call_args.kwargs["params"]["title"] == "translated"


def test_mongo_failure_is_controlled_and_client_closed(logged_api, monkeypatch):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = None
    monkeypatch.setattr(api.modules.library, "search_movie_in_external_api", Mock(return_value={"external_id": 1, "title": "Teste"}))
    api.collection.find_one.side_effect = ServerSelectionTimeoutError("private mongo error")
    response = api.client.post("/library", json={"title": "Teste", "type": "movie"})
    assert response.status_code == 503
    assert "private mongo error" not in response.text
    api.modules.library.MongoClient.return_value.close.assert_called_once()
    api.db.library.rollback.assert_called_once()


@pytest.mark.integration
def test_migration_is_idempotent_and_preserves_existing_rows(postgres_database):
    connection, _ = postgres_database
    with connection.cursor() as cursor:
        # Simula o schema anterior sem as duas colunas.
        cursor.execute("ALTER TABLE userlibrary DROP COLUMN external_api_id, DROP COLUMN content_type")
        cursor.execute("INSERT INTO users (email,password,name) VALUES ('migration@example.com','hash','Nome') RETURNING id")
        user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO userlibrary (user_id,content_id,name) VALUES (%s,'mongo','Duna')", (user_id,))
    connection.commit()
    migration = Path(__file__).resolve().parents[2] / "originais/migrations/001_library_columns.sql"
    with connection.cursor() as cursor:
        for _ in range(2):
            cursor.execute(migration.read_text(encoding="utf-8"))
        cursor.execute("SELECT name, external_api_id, content_type FROM userlibrary")
        assert cursor.fetchall() == [("Duna", None, None)]
