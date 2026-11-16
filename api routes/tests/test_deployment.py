from unittest.mock import MagicMock
import psycopg2
import pytest
import database
from fastapi.testclient import TestClient


def test_import_and_health_do_not_connect_to_database(monkeypatch):
    connect = MagicMock(side_effect=AssertionError('Unexpected database connection'))
    monkeypatch.setattr(database, 'connect_database', connect)
    from main import app
    with TestClient(app) as client:
        assert client.get('/health').json() == {'status': 'ok'}
        assert client.get('/missing-api-endpoint').status_code == 404
    connect.assert_not_called()


@pytest.mark.integration
def test_request_connections_close_after_reads_and_errors(logged_api, postgres_database, monkeypatch):
    _, params = postgres_database
    connections = []
    def connect():
        connection = psycopg2.connect(**params)
        connections.append(connection)
        return connection
    monkeypatch.setattr(database, 'connect_database', connect)
    module = logged_api.modules.library
    scoped = database.RequestConnection()
    monkeypatch.setattr(module, 'connection', scoped)
    monkeypatch.setattr(module, 'cursor', scoped.cursor())
    assert logged_api.client.get('/library').json() == []
    assert logged_api.client.patch('/library/999', json={'rating': 5}).status_code == 404
    assert logged_api.client.get('/library').status_code == 200
    assert len(connections) == 3
    assert all(connection.closed for connection in connections)


@pytest.mark.integration
def test_failed_write_does_not_poison_following_request(api, postgres_database, monkeypatch):
    _, params = postgres_database
    monkeypatch.setattr(database, 'connect_database', lambda: psycopg2.connect(**params))
    module = api.modules.auth
    scoped = database.RequestConnection()
    monkeypatch.setattr(module, 'connection', scoped)
    monkeypatch.setattr(module, 'cursor', scoped.cursor())
    body = {'login': 'deploy_test', 'password': 'SenhaValida123!', 'name': 'Deploy'}
    assert api.client.post('/register', json=body).status_code == 200
    assert api.client.post('/register', json=body).status_code == 409
    assert api.client.post('/register', json={**body, 'login': 'other_test'}).status_code == 200
