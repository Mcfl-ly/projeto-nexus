from bson import ObjectId
import pytest

CONTENT_ID = '0123456789abcdef01234567'

def test_catalog_rejects_foreign_content(logged_api):
    logged_api.db.library.cursor.return_value.fetchall.return_value = []
    response = logged_api.client.post('/get_mongo', json={'ids': [CONTENT_ID]})
    assert response.status_code == 404
    logged_api.modules.library.MongoClient.assert_not_called()

@pytest.mark.parametrize('body', [{}, {'ids': ['invalid']}, {'ids': 'invalid'}])
def test_catalog_validates_ids(logged_api, body):
    assert logged_api.client.post('/get_mongo', json=body).status_code == 422

def test_catalog_returns_only_owned_content(logged_api):
    api = logged_api
    api.db.library.cursor.return_value.fetchall.return_value = [(CONTENT_ID,)]
    api.collection.find.return_value = [{'_id': ObjectId(CONTENT_ID), 'title': 'Livro'}]
    response = api.client.post('/get_mongo', json={'ids': [CONTENT_ID]})
    assert response.status_code == 200
    assert response.json() == [{'_id': CONTENT_ID, 'title': 'Livro'}]
    assert api.db.library.cursor.return_value.execute.call_args.args[1] == ('1',)
