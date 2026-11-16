import datetime

import psycopg2
import pytest
from argon2 import PasswordHasher


@pytest.mark.integration
def test_cadastro_valido_persiste_no_postgresql(integration_client, postgres_database):
    dados = {
        "login": "integracao_example_com",
        "password": "SenhaIntegracao123!",
        "name": "Usuario integracao",
    }
    resposta = integration_client.post("/register", json=dados)
    assert resposta.status_code == 200
    assert resposta.json() is None

    # Outra conexao so enxerga o registro se a rota fez commit.
    _, params = postgres_database
    verification = psycopg2.connect(**params)
    try:
        with verification.cursor() as cursor:
            cursor.execute(
                "SELECT login, password, name, created_at FROM users WHERE login = %s",
                (dados["login"],),
            )
            registros = cursor.fetchall()
        assert len(registros) == 1
        login, senha_hash, nome, data = registros[0]
        assert login == dados["login"]
        assert nome == dados["name"]
        assert data == datetime.date.today()
        assert senha_hash != dados["password"]
        assert PasswordHasher().verify(senha_hash, dados["password"])
    finally:
        verification.close()
