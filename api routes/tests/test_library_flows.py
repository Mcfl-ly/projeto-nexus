import datetime
from unittest.mock import Mock

import psycopg2
import pytest
import requests


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
@pytest.mark.parametrize("cached", [True, False])
def test_add_content_links_to_authenticated_user(logged_api, monkeypatch, kind, cached):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = None
    doc = {"_id": "mongo123", "external_id": "external123", "title": "teste", "type": kind}
    api.collection.find_one.return_value = doc if cached else None
    monkeypatch.setattr(api.modules.library, f"search_{kind}_in_external_api", Mock(return_value=dict(doc)))
    response = api.client.post("/library", json={"title": "teste", "type": kind, "user_id": 999})
    assert response.status_code == 200
    values = api.db.library.cursor.return_value.execute.call_args.args[1]
    assert values[0] == 1
    assert values[1:3] == ("mongo123", "teste")
    assert values[-1] == kind
    api.db.library.commit.assert_called_once()
    assert api.collection.insert_one.call_count == (0 if cached else 1)


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
def test_duplicate_library_content_does_not_insert(logged_api, monkeypatch, kind):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = (1,)
    search = Mock()
    monkeypatch.setattr(api.modules.library, f"search_{kind}_in_external_api", search)
    response = api.client.post("/library", json={"title": "teste", "type": kind})
    assert response.status_code == 200
    assert "existe" in response.json()
    search.assert_not_called()
    api.collection.insert_one.assert_not_called()
    api.db.library.commit.assert_not_called()


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
def test_manual_content_insert(logged_api, kind):
    api = logged_api
    api.collection.find_one.return_value = {"_id": "manual123", "title": "Manual"}
    response = api.client.post("/library/manual", json={"title": "Manual", "type": kind, "author": ["Autor"]})
    assert response.status_code == 200
    api.collection.insert_one.assert_called_once()
    values = api.db.library.cursor.return_value.execute.call_args.args[1]
    assert values[0] == "1" and values[1] == "manual123" and values[-1] == kind
    api.db.library.commit.assert_called_once()


@pytest.mark.parametrize("route", ["/library", "/library/manual"])
@pytest.mark.parametrize("payload", [{}, {"title": "Teste"}, {"type": "book"}])
def test_library_required_fields(logged_api, route, payload):
    assert logged_api.client.post(route, json=payload).status_code == 422
    logged_api.db.library.commit.assert_not_called()


@pytest.mark.parametrize("route", ["/library", "/library/manual"])
def test_unknown_content_type_rejected(logged_api, route):
    logged_api.collection.find_one.return_value = {"_id": "fake", "title": "Teste"}
    assert logged_api.client.post(route, json={"title": "Teste", "type": "invalid"}).status_code == 422
    logged_api.db.library.commit.assert_not_called()


def test_list_library_filters_current_user(logged_api):
    api = logged_api
    row = [1, 1, "mongo", "Duna", "Quero Ler", None, "2026-01-01"]
    api.db.library.cursor.return_value.fetchall.return_value = [row]
    response = api.client.get("/library?user_id=999")
    assert response.status_code == 200
    assert response.json() == [row]
    assert api.db.library.cursor.return_value.execute.call_args.args[1] == ("1",)


@pytest.mark.parametrize("payload,expected", [
    ({"status": "Lido"}, ("Lido", 3)), ({"rating": 5}, ("Quero Ler", 5)),
    ({"status": "Lido", "rating": 5}, ("Lido", 5)),
])
def test_update_library_preserves_unspecified_fields(logged_api, payload, expected):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = ("Quero Ler", 3)
    response = api.client.patch("/library/7", json=payload)
    assert response.status_code == 200
    assert response.json() == dict(zip(("status", "rating"), expected))
    assert api.db.library.cursor.return_value.execute.call_args.args[1] == (*expected, "1", 7)
    api.db.library.commit.assert_called_once()


def test_update_missing_or_other_users_content(logged_api):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = None
    assert api.client.patch("/library/999", json={"rating": 5}).status_code == 404
    api.db.library.cursor.return_value.execute.assert_called_once()
    assert api.db.library.cursor.return_value.execute.call_args.args[1] == ("1", 999)
    api.db.library.commit.assert_not_called()


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_library_id_must_be_integer(logged_api, method):
    assert logged_api.client.request(method, "/library/not-a-number", json={"rating": 5}).status_code == 422


def test_library_rating_must_be_number(logged_api):
    assert logged_api.client.patch("/library/1", json={"rating": "invalid"}).status_code == 422


def test_delete_library_filters_owner(logged_api):
    api = logged_api
    assert api.client.delete("/library/7").status_code == 200
    query, values = api.db.library.cursor.return_value.execute.call_args.args
    assert "user_id = %s" in query and "id = %s" in query
    assert values == ("1", 7)
    api.db.library.commit.assert_called_once()


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
def test_library_conflict_rolls_back(logged_api, monkeypatch, kind):
    api = logged_api
    monkeypatch.setattr(api.modules.library, f"add_{kind}_to_library", Mock(side_effect=psycopg2.errors.UniqueViolation("duplicate")))
    assert api.client.post("/library", json={"title": "teste", "type": kind}).status_code == 409
    api.db.library.rollback.assert_called_once()


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
@pytest.mark.parametrize("failure", ["timeout", "http_error", "not_found"])
def test_external_failures_are_controlled(logged_api, monkeypatch, kind, failure):
    api = logged_api
    api.db.library.cursor.return_value.fetchone.return_value = None
    monkeypatch.setattr(api.modules.library, "get_igdb_token", Mock(return_value="fake-token"))
    monkeypatch.setattr(api.modules.library, "translate_title", Mock(side_effect=lambda value: value))
    if failure == "timeout":
        response = Mock(side_effect=requests.Timeout("test timeout"))
        expected = (502, 503, 504)
    else:
        body = {"movie": {"results": []}, "game": [], "book": {"docs": []}}[kind]
        response = Mock(return_value=Mock(status_code=503 if failure == "http_error" else 200, json=Mock(return_value=body)))
        expected = (502, 503, 504) if failure == "http_error" else (404,)
    monkeypatch.setattr(api.modules.library.requests, "post" if kind == "game" else "get", response)
    result = api.client.post("/library", json={"title": "missing", "type": kind})
    assert result.status_code in expected
    api.db.library.commit.assert_not_called()


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
def test_external_response_mapping(api, monkeypatch, kind):
    library = api.modules.library
    monkeypatch.setattr(library, "get_igdb_token", Mock(return_value="fake"))
    monkeypatch.setattr(library, "translate_title", Mock(side_effect=lambda value: value))
    bodies = {
        "movie": {"results": [{"id": 42, "title": " Ação ", "original_title": "Action", "overview": "Resumo", "release_date": "2020-01-01", "genre_ids": [28, 99999], "poster_path": None}]},
        "game": [{"id": 42, "name": " Ação ", "first_release_date": 1577880000, "genres": [{"name": "Adventure"}], "cover": {"image_id": "abc"}}],
        "book": {"docs": [{"key": "OL42", "title": " Ação ", "author_name": ["Autor"], "first_publish_year": 2020, "subject": ["fantasy", "fantasia"], "cover_i": 42}]},
    }
    monkeypatch.setattr(library.requests, "post" if kind == "game" else "get", Mock(return_value=Mock(status_code=200, json=Mock(return_value=bodies[kind]))))
    result = getattr(library, f"search_{kind}_in_external_api")("Ação")
    assert result["type"] == kind
    assert result["title"] == "acao"
    assert result["external_id"] == ("OL42" if kind == "book" else 42)
    if kind == "movie":
        assert result["genres"] == ["Ação"] and result["poster"] is None
    if kind == "book":
        assert result["genres"] == ["Fantasia"]


def test_igdb_token_is_cached(api, monkeypatch):
    request = Mock(return_value=Mock(status_code=200, json=Mock(return_value={"access_token": "fake-access"})))
    monkeypatch.setattr(api.modules.library.requests, "post", request)
    assert api.modules.library.get_igdb_token() == "fake-access"
    assert api.modules.library.get_igdb_token() == "fake-access"
    request.assert_called_once()


@pytest.mark.parametrize("title,expected", [("  AÇÃO  ", "acao"), ("Duna", "duna"), ("", "")])
def test_normalize_titles(api, title, expected):
    assert api.modules.library.normalize_text(title) == expected
