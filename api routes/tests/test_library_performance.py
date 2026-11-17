from bson import ObjectId
from unittest.mock import MagicMock
import catalog

ID1 = '0123456789abcdef01234567'
ID2 = '1123456789abcdef01234567'

def test_full_library_requires_auth(api):
    assert api.client.get('/library/full').status_code == 401
    api.db.library.cursor.return_value.execute.assert_not_called()

def test_empty_full_library_skips_mongo(logged_api):
    api = logged_api
    api.db.library.cursor.return_value.fetchall.return_value = []
    assert api.client.get('/library/full').json() == {'library': [], 'contents': []}
    api.modules.library.MongoClient.assert_not_called()

def test_full_library_batches_and_deduplicates_owned_ids(logged_api):
    api = logged_api
    rows = [[1, 1, ID1, 'A', 'Quero Ler', None, None, None, 'book', False],
            [2, 1, ID2, 'B', 'Quero Ler', None, None, None, 'book', True],
            [3, 1, ID1, 'A', 'Lido', None, None, None, 'book', False]]
    api.db.library.cursor.return_value.fetchall.return_value = rows
    api.collection.find.return_value = [{'_id': ObjectId(ID2), 'title': 'B'}, {'_id': ObjectId(ID1), 'title': 'A'}]
    result = api.client.get('/library/full')
    assert result.status_code == 200
    assert result.json()['library'] == rows
    assert {doc['_id'] for doc in result.json()['contents']} == {ID1, ID2}
    api.collection.find.assert_called_once_with({'_id': {'$in': [ObjectId(ID1), ObjectId(ID2)]}})
    api.collection.find_one.assert_not_called()
    query, args = api.db.library.cursor.return_value.execute.call_args.args
    assert 'WHERE user_id = %s' in query and args == ('1',)

def test_catalog_batch_preserves_order_missing_and_duplicate_ids(logged_api):
    api = logged_api
    api.db.library.cursor.return_value.fetchall.return_value = [(ID1,), (ID2,)]
    api.collection.find.return_value = [{'_id': ObjectId(ID2), 'title': 'B'}]
    result = api.client.post('/get_mongo', json={'ids': [ID1, ID2, ID2]})
    assert result.json() == [None, {'_id': ID2, 'title': 'B'}, {'_id': ID2, 'title': 'B'}]
    api.collection.find.assert_called_once()
    api.collection.find_one.assert_not_called()

def test_lightweight_profile_does_not_query_library(logged_api):
    api = logged_api
    api.db.users.cursor.return_value.fetchone.return_value = (1, 'test', 'private', 'Nome', None)
    result = api.client.get('/users/me?include_content=false')
    assert result.status_code == 200 and result.json()['content'] == []
    api.db.users.cursor.return_value.execute.assert_called_once()

def test_catalog_pool_is_reused_and_closed_at_shutdown(monkeypatch):
    catalog.close_catalog()
    factory = MagicMock()
    monkeypatch.setattr(catalog, 'MongoClient', factory)
    first = catalog.open_catalog('mongodb://example.invalid')
    second = catalog.open_catalog('mongodb://example.invalid')
    first.close()
    second.close()
    factory.assert_called_once()
    factory.return_value.close.assert_not_called()
    catalog.close_catalog()
    factory.return_value.close.assert_called_once()
