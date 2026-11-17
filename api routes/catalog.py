from threading import Lock
from pymongo import MongoClient

_clients = {}
_lock = Lock()

class CatalogHandle:
    """A route handle; closing it preserves the process-wide connection pool."""
    def __init__(self, client):
        self.client = client
    def __getitem__(self, name):
        return self.client[name]
    def close(self):
        pass

def open_catalog(uri, **options):
    with _lock:
        if uri not in _clients:
            _clients[uri] = MongoClient(uri, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
        return CatalogHandle(_clients[uri])

def close_catalog():
    with _lock:
        clients = list(_clients.values())
        _clients.clear()
    for client in clients:
        client.close()
