from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Impede a abertura de uma conexão real ao importar as rotas.
    with patch("psycopg2.connect"):
        from routers.auth.routes import router

        app = FastAPI()
        app.include_router(router)

        with TestClient(app) as test_client:
            yield test_client


def test_cadastro_rejeita_senha_curta(client):
    resposta = client.post(
        "/register",
        json={
            "email": "teste@example.com",
            "password": "123",
            "name": "Usuario teste",
        },
    )

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    assert any(erro["loc"] == ["body", "password"] for erro in erros)


def test_cadastro_rejeita_email_invalido(client):
    resposta = client.post(
        "/register",
        json={
            "email": "email-invalido",
            "password": "senha12345",
            "name": "Usuario teste",
        },
    )

    assert resposta.status_code == 422
    erros = resposta.json()["detail"]
    assert any(erro["loc"] == ["body", "email"] for erro in erros)