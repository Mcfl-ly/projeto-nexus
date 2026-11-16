"""A dedicated PostgreSQL connection and cursor for each route invocation."""
from contextlib import contextmanager
from contextvars import ContextVar
import os
import psycopg2
import settings  # Loads local configuration without overriding hosted variables.

_state = ContextVar("database_request", default=None)

def connect_database():
    url = os.getenv("DATABASE_URL")
    if url:
        return psycopg2.connect(url, connect_timeout=10)
    return psycopg2.connect(dbname=os.getenv("DBNAME"), host=os.getenv("HOST"),
        port=os.getenv("DB_PORT", os.getenv("PORT", "5432")), user=os.getenv("USER"),
        password=os.getenv("PASSWORD"), connect_timeout=10)

def _connection():
    state = _state.get()
    if state is None:
        raise RuntimeError("Database access outside request scope")
    if state["connection"] is None:
        state["connection"] = connect_database()
    return state["connection"]

@contextmanager
def request_scope():
    state = {"connection": None, "cursor": None}
    token = _state.set(state)
    try:
        yield
    finally:
        try:
            if state["connection"] is not None:
                try:
                    # Also ends read-only transactions and unsuccessful requests.
                    state["connection"].rollback()
                finally:
                    state["connection"].close()
        finally:
            _state.reset(token)

class RequestConnection:
    def cursor(self):
        return RequestCursor()
    def commit(self):
        _connection().commit()
    def rollback(self):
        state = _state.get()
        if state is not None and state["connection"] is not None:
            state["connection"].rollback()

class RequestCursor:
    def __getattr__(self, name):
        connection = _connection()
        state = _state.get()
        if state["cursor"] is None:
            state["cursor"] = connection.cursor()
        return getattr(state["cursor"], name)
