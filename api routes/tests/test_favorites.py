import psycopg2
import pytest


@pytest.mark.parametrize('favorite', [True, False])
def test_favorite_saves_only_current_users_item(logged_api, favorite):
    api = logged_api
    cursor = api.db.library.cursor.return_value
    cursor.fetchone.return_value = (favorite,)
    response = api.client.patch('/library/7/favorite', json={'favorite': favorite, 'user_id': 999})
    assert response.status_code == 200
    assert response.json() == {'favorite': favorite}
    query, params = cursor.execute.call_args.args
    assert 'WHERE user_id = %s AND id = %s' in query
    assert params == (favorite, '1', 7)
    api.db.library.commit.assert_called_once()


def test_favorite_requires_authentication(api):
    assert api.client.patch('/library/7/favorite', json={'favorite': True}).status_code == 401
    api.db.library.cursor.return_value.execute.assert_not_called()


def test_missing_or_foreign_favorite_returns_404(logged_api):
    logged_api.db.library.cursor.return_value.fetchone.return_value = None
    assert logged_api.client.patch('/library/7/favorite', json={'favorite': True}).status_code == 404
    logged_api.db.library.commit.assert_not_called()
    logged_api.db.library.rollback.assert_called_once()


@pytest.mark.parametrize('body', [{}, {'favorite': None}, {'favorite': 'false'}, {'favorite': 1}])
def test_favorite_requires_boolean(logged_api, body):
    assert logged_api.client.patch('/library/7/favorite', json=body).status_code == 422
    logged_api.db.library.cursor.return_value.execute.assert_not_called()


def test_favorite_database_failure_rolls_back(logged_api):
    logged_api.db.library.cursor.return_value.execute.side_effect = psycopg2.OperationalError('private')
    response = logged_api.client.patch('/library/7/favorite', json={'favorite': True})
    assert response.status_code == 503
    assert 'private' not in response.text
    logged_api.db.library.rollback.assert_called_once()


def test_library_includes_favorite(logged_api):
    row = [7, 1, 'mongo', 'Titulo', 'Quero Ler', None, '2026-11-16', None, 'book', True]
    logged_api.db.library.cursor.return_value.fetchall.return_value = [row]
    response = logged_api.client.get('/library')
    assert response.status_code == 200
    assert response.json()[0][9] is True


@pytest.mark.integration
def test_favorites_persist_and_are_isolated(real_api, access_token):
    api = real_api
    with api.connection.cursor() as cursor:
        cursor.execute("INSERT INTO users (login,password,name) VALUES ('fav1_example_com','hash','A'),('fav2_example_com','hash','B') RETURNING id")
        alice, bob = [row[0] for row in cursor.fetchall()]
        cursor.execute("INSERT INTO userlibrary (user_id,content_id,name) VALUES (%s,'mongo','Livro') RETURNING id", (alice,))
        item = cursor.fetchone()[0]
    api.connection.commit()
    api.client.cookies.set('access_token', access_token(bob))
    assert api.client.patch(f'/library/{item}/favorite', json={'favorite': True}).status_code == 404
    api.client.cookies.set('access_token', access_token(alice))
    assert api.client.get('/library').json()[0][9] is False
    for favorite in [True, False]:
        assert api.client.patch(f'/library/{item}/favorite', json={'favorite': favorite}).status_code == 200
        assert api.client.get('/library').json()[0][9] is favorite
