import datetime

from argon2 import PasswordHasher


def test_cadastro_valido_insere_usuario_e_confirma_transacao(client, mock_db):
    dados = {
        "email": "cadastro@example.com",
        "password": "SenhaValida123!",
        "name": "Usuario teste",
    }
    resposta = client.post("/register", json=dados)

    assert resposta.status_code == 200
    assert resposta.json() is None  # Contrato atual da rota.
    cursor = mock_db.cursor.return_value
    cursor.execute.assert_called_once()
    consulta, parametros = cursor.execute.call_args.args
    assert "INSERT INTO users" in consulta
    email, senha_hash, nome, data = parametros
    assert email == dados["email"]
    assert nome == dados["name"]
    assert data == datetime.date.today()
    assert senha_hash != dados["password"]
    assert PasswordHasher().verify(senha_hash, dados["password"])
    mock_db.commit.assert_called_once_with()
