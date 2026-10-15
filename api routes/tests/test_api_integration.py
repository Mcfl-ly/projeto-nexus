import datetime
from unittest.mock import Mock, patch

import psycopg2
import pytest
from argon2 import PasswordHasher


pytestmark = pytest.mark.integration
DATA = {"email": "alice@example.com", "password": "SenhaValida123!", "name": "Alice"}


def register_and_login(api):
    assert api.client.post("/register", json=DATA).status_code == 200
    assert api.client.post("/login", json=DATA).status_code == 200


def fetch(api, query, args=()):
    connection = psycopg2.connect(**api.params)
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, args)
            return cursor.fetchall()
    finally:
        connection.close()


def test_register_login_profile_end_to_end(real_api):
    api = real_api
    register_and_login(api)
    response = api.client.get("/users/me")
    assert response.status_code == 200
    assert response.json()["email"] == DATA["email"]
    assert "password" not in response.json()
    rows = fetch(api, "SELECT token, revoked FROM refreshtoken")
    assert len(rows) == 1 and rows[0][1] is False
    assert PasswordHasher().verify(rows[0][0], api.client.cookies["refresh_token"])


def test_duplicate_register_does_not_poison_next_request(real_api):
    api = real_api
    assert api.client.post("/register", json=DATA).status_code == 200
    duplicate = api.client.post("/register", json=DATA)
    assert duplicate.status_code == 409
    assert api.client.post("/register", json={**DATA, "email": "bob@example.com"}).status_code == 200
    assert len(fetch(api, "SELECT id FROM users")) == 2


def test_username_update_persists(real_api):
    api = real_api
    register_and_login(api)
    assert api.client.patch("/users/me", json={"username": "Alice Nova"}).status_code == 200
    assert fetch(api, "SELECT name FROM users WHERE email=%s", (DATA["email"],)) == [("Alice Nova",)]


def test_password_change_rejects_old_and_accepts_new(real_api):
    api = real_api
    register_and_login(api)
    assert api.client.patch("/users/me/password", json={"password": "NovaSenha123!"}).status_code == 200
    assert api.client.post("/login", json=DATA).status_code == 401
    assert api.client.post("/login", json={**DATA, "password": "NovaSenha123!"}).status_code == 200


def test_logout_revokes_refresh_in_database(real_api):
    api = real_api
    register_and_login(api)
    previous = api.client.cookies["refresh_token"]
    assert api.client.post("/logout").status_code == 200
    assert "refresh_token" not in api.client.cookies
    assert "access_token" not in api.client.cookies
    assert fetch(api, "SELECT revoked FROM refreshtoken") == [(True,)]
    api.client.cookies.set("refresh_token", previous)
    assert api.client.post("/refresh").status_code == 401


def test_refresh_persists_rotation_and_rejects_replay(real_api):
    api = real_api
    # Congela somente a emissao do refresh para testar replay sem depender
    # da velocidade da maquina ou de atravessar a virada de um segundo.
    original = api.modules.auth.create_refresh_token
    fixed = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    def fixed_refresh(user_id):
        with patch.object(api.modules.auth.datetime, "datetime") as clock:
            clock.now.return_value = fixed
            return original(user_id)
    with patch.object(api.modules.auth, "create_refresh_token", side_effect=fixed_refresh):
        register_and_login(api)
        old = api.client.cookies["refresh_token"]
        response = api.client.post("/refresh")
    assert response.status_code == 200
    rows = fetch(api, "SELECT revoked FROM refreshtoken ORDER BY id")
    assert rows == [(True,), (False,)]
    api.client.cookies.clear()
    api.client.cookies.set("refresh_token", old)
    assert api.client.post("/refresh").status_code == 401


def test_account_deletion_removes_related_records(real_api):
    api = real_api
    register_and_login(api)
    with api.connection.cursor() as cursor:
        cursor.execute("INSERT INTO userlibrary (user_id, content_id, name) SELECT id, 'mongo-test', 'Duna' FROM users WHERE email=%s", (DATA["email"],))
    api.connection.commit()
    assert api.client.delete("/users/me/delete").status_code == 200
    for table in ("users", "refreshtoken", "userlibrary"):
        assert fetch(api, f"SELECT COUNT(*) FROM {table}") == [(0,)]
    assert api.client.post("/login", json=DATA).status_code == 401


def test_library_owner_isolation_and_crud(real_api, access_token):
    api = real_api
    assert api.client.post("/register", json=DATA).status_code == 200
    assert api.client.post("/register", json={**DATA, "email": "bob@example.com"}).status_code == 200
    alice, bob = [row[0] for row in fetch(api, "SELECT id FROM users ORDER BY id")]
    with api.connection.cursor() as cursor:
        cursor.execute("INSERT INTO userlibrary (user_id,content_id,name,status,rating) VALUES (%s,'mongo-test','Duna','Quero Ler',2) RETURNING id", (alice,))
        item = cursor.fetchone()[0]
    api.connection.commit()
    api.client.cookies.set("access_token", access_token(bob))
    assert api.client.get("/library").json() == []
    assert api.client.patch(f"/library/{item}", json={"rating": 5}).status_code == 404
    assert api.client.delete(f"/library/{item}").status_code in (200, 204, 404)
    assert fetch(api, "SELECT rating FROM userlibrary WHERE id=%s", (item,)) == [(2.0,)]
    api.client.cookies.clear()
    api.client.cookies.set("access_token", access_token(alice))
    assert len(api.client.get("/library").json()) == 1
    assert api.client.patch(f"/library/{item}", json={"rating": 5}).status_code == 200
    assert fetch(api, "SELECT rating FROM userlibrary WHERE id=%s", (item,)) == [(5.0,)]
    assert api.client.delete(f"/library/{item}").status_code == 200
    assert fetch(api, "SELECT id FROM userlibrary") == []


@pytest.mark.parametrize("kind", ["movie", "game", "book"])
def test_library_add_with_repository_schema(real_api, monkeypatch, kind):
    api = real_api
    register_and_login(api)
    doc = {"_id": "mongo123", "external_id": "42", "title": "Teste", "type": kind}
    api.collection.find_one.return_value = doc
    monkeypatch.setattr(api.modules.library, f"search_{kind}_in_external_api", Mock(return_value=doc))
    response = api.client.post("/library", json={"title": "Teste", "type": kind})
    assert response.status_code == 200, "A rota precisa funcionar com o schema SQL versionado no projeto"
    assert len(fetch(api, "SELECT id FROM userlibrary")) == 1


def test_profile_with_library_using_repository_schema(real_api):
    api = real_api
    register_and_login(api)
    with api.connection.cursor() as cursor:
        cursor.execute("INSERT INTO userlibrary (user_id,content_id,name) SELECT id,'mongo-test','Duna' FROM users")
    api.connection.commit()
    response = api.client.get("/users/me")
    assert response.status_code == 200
    assert len(response.json()["content"]) == 1


def test_expired_refresh_rejected_in_database(real_api):
    api = real_api
    register_and_login(api)
    with api.connection.cursor() as cursor:
        cursor.execute("UPDATE refreshtoken SET expires_at=CURRENT_DATE - 1")
    api.connection.commit()
    assert api.client.post("/refresh").status_code == 401
    assert fetch(api, "SELECT COUNT(*) FROM refreshtoken") == [(1,)]
