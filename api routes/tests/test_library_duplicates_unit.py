from unittest.mock import MagicMock, Mock
import pytest

@pytest.fixture
def library(api_modules, monkeypatch):
    module = api_modules.library
    connection = MagicMock()
    monkeypatch.setattr(module, 'connection', connection)
    monkeypatch.setattr(module, 'cursor', connection.cursor.return_value)
    monkeypatch.setattr(module, 'MongoClient', MagicMock())
    monkeypatch.setenv('DATABASE', 'test')
    monkeypatch.setenv('COLECAO', 'test')
    return module

@pytest.mark.parametrize('kind', ['movie', 'game', 'book'])
def test_external_duplicate_identity(library, kind):
    library.cursor.fetchone.side_effect = [None, (2,)]
    search = Mock(return_value={'external_id': 165, 'title': 'titulo normalizado'})
    data = library.ContentRequest(title='Outro Titulo', type=kind)
    assert 'existe' in library._add_catalog_content(data, '1', search, 'Conteudo', 'Quero')
    assert library.cursor.execute.call_args.args[1] == (1, '165', kind)
    library.MongoClient.assert_not_called()
    library.connection.commit.assert_not_called()

@pytest.mark.parametrize('kind', ['movie', 'game', 'book'])
def test_manual_duplicate_legacy_accents(library, kind):
    library.cursor.fetchall.return_value = [('  AÇÃO  ',)]
    data = library.ManualContent(title='acao', type=kind)
    assert 'existe' in library._add_manual_content(data, '1', 'Conteudo', 'Quero')
    library.MongoClient.assert_not_called()
    library.connection.commit.assert_not_called()

@pytest.mark.parametrize('kind', ['movie', 'game', 'book'])
@pytest.mark.parametrize('cached', [True, False])
def test_manual_document_identity(library, kind, cached):
    library.cursor.fetchall.return_value = []
    collection = library.MongoClient.return_value.__getitem__.return_value.__getitem__.return_value
    collection.find_one.return_value = {'_id': 'existing'} if cached else None
    collection.insert_one.return_value.inserted_id = 'new'
    data = library.ManualContent(title=' Ação ', type=kind)
    assert 'sucesso' in library._add_manual_content(data, '1', 'Conteudo', 'Quero')
    collection.find_one.assert_called_once_with({
        'title': 'acao', 'type': kind, 'external_id': {'$exists': False}})
    assert collection.insert_one.call_count == (0 if cached else 1)
    values = library.cursor.execute.call_args.args[1]
    assert values[1:3] == ('existing' if cached else 'new', 'acao')
    assert values[-1] == kind
    library.connection.commit.assert_called_once()
    library.MongoClient.return_value.close.assert_called_once()
