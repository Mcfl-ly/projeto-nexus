import datetime

import psycopg2
import pytest
from argon2 import PasswordHasher


@pytest.mark.integration
def test_cadastro_valido_persiste_no_postgresql(integration_client, postgres_database):
    dados = {
        "email": "integracao@example.com",
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
                "SELECT email, password, name, created_at FROM users WHERE email = %s",
                (dados["email"],),
            )
            registros = cursor.fetchall()
        assert len(registros) == 1
        email, senha_hash, nome, data = registros[0]
        assert email == dados["email"]
        assert nome == dados["name"]
        assert data == datetime.date.today()
        assert senha_hash != dados["password"]
        assert PasswordHasher().verify(senha_hash, dados["password"])
    finally:
        verification.close()
