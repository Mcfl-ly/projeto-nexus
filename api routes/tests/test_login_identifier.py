from pathlib import Path
import datetime
import pytest
from argon2 import PasswordHasher


@pytest.mark.parametrize('login', ['ab', 'nome com espaço', 'nome@example.com', 'x' * 51])
def test_register_rejects_invalid_login(api, login):
    response = api.client.post('/register', json={'login': login, 'name': 'Nome', 'password': 'SenhaValida123'})
    assert response.status_code == 422
    api.db.auth.cursor.return_value.execute.assert_not_called()


def test_register_normalizes_login(api):
    response = api.client.post('/register', json={'login': '  Paulo_Gamer  ', 'name': 'Paulo', 'password': 'SenhaValida123'})
    assert response.status_code == 200
    query, values = api.db.auth.cursor.return_value.execute.call_args.args
    assert '(login, password, name' in query
    assert values[0] == 'paulo_gamer'


@pytest.mark.parametrize('identifier', ['Paulo_Gamer', 'old@example.com'])
def test_login_normalizes_identifier_and_accepts_legacy_accounts(api, identifier):
    api.db.auth.cursor.return_value.fetchone.return_value = (1, identifier.lower(), PasswordHasher().hash('SenhaValida123'), 'Paulo', datetime.date.today())
    assert api.client.post('/login', json={'login': '  ' + identifier + '  ', 'password': 'SenhaValida123'}).status_code == 200
    query, values = api.db.auth.cursor.return_value.execute.call_args_list[0].args
    assert 'lower(login)' in query
    assert values == (identifier.lower(),)


@pytest.mark.integration
def test_login_migration_preserves_existing_accounts(postgres_database):
    connection, _ = postgres_database
    migration = Path(__file__).resolve().parents[1] / 'migrations/004_users_login.sql'
    with connection.cursor() as cursor:
        cursor.execute('ALTER TABLE users RENAME COLUMN login TO email')
        cursor.execute("INSERT INTO users(email,password,name) VALUES ('legacy@example.com','hash','Nome')")
    connection.commit()
    with connection.cursor() as cursor:
        for _ in range(2):
            cursor.execute(migration.read_text(encoding='utf-8'))
        cursor.execute('SELECT login, password, name FROM users')
        assert cursor.fetchall() == [('legacy@example.com', 'hash', 'Nome')]
        cursor.execute("SELECT indexname FROM pg_indexes WHERE tablename='users' AND indexname='users_login_lower_unique'")
        assert cursor.fetchone() is not None
