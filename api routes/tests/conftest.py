import importlib
import os
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4
from contextlib import ExitStack
from types import SimpleNamespace, ModuleType
from unittest.mock import MagicMock
import sys
import datetime
import jwt
import requests

import psycopg2
from psycopg2 import sql
import pytest
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.testclient import TestClient


def pytest_addoption(parser):
    parser.addoption(
        "--run-integration", action="store_true", default=False,
        help="Cria um banco PostgreSQL temporario, testa e remove o banco.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "integration: usa PostgreSQL real")


def pytest_collection_modifyitems(config, items):
    if not config.getoption("--run-integration"):
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(pytest.mark.skip(reason="Use --run-integration"))


@pytest.fixture(scope="session")
def auth_module():
    # A importacao original abre uma conexao global. Isolamos esse efeito.
    with patch("psycopg2.connect"):
        return importlib.import_module("routers.auth.routes")


@pytest.fixture
def mock_db(auth_module):
    # Substituir os atributos por teste evita compartilhar mocks em cache.
    with patch.object(auth_module, "connection") as connection:
        with patch.object(auth_module, "cursor", connection.cursor.return_value):
            yield connection


@pytest.fixture
def client(auth_module, mock_db):
    app = FastAPI()
    app.include_router(auth_module.router)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def postgres_database():
    # Credenciais permanecem locais; nao mostramos a URL nem o .env.
    values = dotenv_values(Path(__file__).resolve().parents[1] / ".env")
    def setting(name):
        return values.get(name) or os.getenv(name)

    params = {
        "host": setting("HOST"), "port": setting("PORT"),
        "user": setting("USER"), "password": setting("PASSWORD"),
        "dbname": setting("DBNAME"), "connect_timeout": 5,
    }
    admin = psycopg2.connect(**params)
    admin.autocommit = True
    database_name = "nexus_pytest_" + uuid4().hex
    created = False
    connection = None
    try:
        with admin.cursor() as cursor:
            cursor.execute(sql.SQL("CREATE DATABASE {} TEMPLATE template0").format(
                sql.Identifier(database_name)
            ))
        created = True
        test_params = {**params, "dbname": database_name}
        connection = psycopg2.connect(**test_params)
        # Usa as tres tabelas do script real, sem os INSERTs de exemplo.
        schema_file = Path(__file__).resolve().parents[2] / "originais" / "sql_proj.psql"
        ddl_parts = schema_file.read_text(encoding="utf-8-sig").split(";")[:3]
        users_ddl = ddl_parts[0]
        if not users_ddl.strip().lower().startswith("create table users"):
            raise ValueError("O script SQL deve comecar com CREATE TABLE users")
        with connection.cursor() as cursor:
            for statement in ddl_parts:
                cursor.execute(statement)
        connection.commit()
        yield connection, test_params
    finally:
        try:
            if connection is not None:
                connection.close()
            if created:
                with admin.cursor() as cursor:
                    cursor.execute(sql.SQL("DROP DATABASE {}").format(
                        sql.Identifier(database_name)
                    ))
        finally:
            admin.close()


@pytest.fixture
def integration_client(auth_module, postgres_database):
    connection, _ = postgres_database
    with connection.cursor() as cursor:
        with patch.object(auth_module, "connection", connection):
            with patch.object(auth_module, "cursor", cursor):
                app = FastAPI()
                app.include_router(auth_module.router)
                with TestClient(app) as test_client:
                    yield test_client


TEST_SECRET = "nexus-test-only-secret-never-used-in-production-123456"


class ApiTestContext(SimpleNamespace):
    def __repr__(self):
        # O pytest inclui repr dos objetos nas falhas. Nao exponha params
        # de conexao do PostgreSQL, que contem credenciais locais.
        return "<Nexus API test context>"


@pytest.fixture(autouse=True)
def block_external_http(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("HTTP externo bloqueado: use mock no teste")
    monkeypatch.setattr(requests.sessions.Session, "request", blocked)


@pytest.fixture(scope="session")
def api_modules(auth_module):
    # Argos faz download ao importar o modulo. Simulamos apenas a dependencia
    # de traducao; todas as funcoes e rotas do Nexus continuam reais.
    argos = ModuleType("argostranslate")
    package = ModuleType("argostranslate.package")
    translate = ModuleType("argostranslate.translate")
    package.update_package_index = MagicMock()
    package.get_available_packages = MagicMock(return_value=[SimpleNamespace(
        from_code="pt", to_code="en", download=MagicMock(return_value="mock-package")
    )])
    package.install_from_path = MagicMock()
    translate.translate = MagicMock(side_effect=lambda text, *args: text)
    argos.package, argos.translate = package, translate
    with patch.dict(sys.modules, {
        "argostranslate": argos, "argostranslate.package": package,
        "argostranslate.translate": translate,
    }), patch("psycopg2.connect"), patch("pymongo.MongoClient"):
        users = importlib.import_module("routers.users.routes")
        library = importlib.import_module("routers.library.routes")
    return SimpleNamespace(auth=auth_module, users=users, library=library)


@pytest.fixture
def api(api_modules, monkeypatch):
    modules = api_modules
    databases = {}
    app = FastAPI()
    for name in ("auth", "users", "library"):
        module = getattr(modules, name)
        connection = MagicMock()
        databases[name] = connection
        monkeypatch.setattr(module, "connection", connection)
        monkeypatch.setattr(module, "cursor", connection.cursor.return_value)
        monkeypatch.setattr(module, "secret_key", TEST_SECRET)
        monkeypatch.setattr(module, "algorithm", "HS256")
        app.include_router(module.router)
    mongo = MagicMock()
    monkeypatch.setattr(modules.library, "MongoClient", mongo)
    monkeypatch.setattr(modules.library, "IGDB_TOKEN", None)
    monkeypatch.delattr(modules.library, "response", raising=False)
    monkeypatch.setenv("DATABASE", "nexus_test")
    monkeypatch.setenv("COLECAO", "contents_test")
    # Evita que mensagens de erro incluam credenciais reais de APIs.
    for key in ("TWITCH_CLIENT_ID", "TWITCH_CLIENT_SECRET", "TMDB_KEY"):
        monkeypatch.setenv(key, "test-placeholder")
    with TestClient(app, base_url="https://testserver", raise_server_exceptions=False) as client:
        yield ApiTestContext(
            client=client, modules=modules, db=SimpleNamespace(**databases),
            collection=mongo.return_value.__getitem__.return_value.__getitem__.return_value,
        )


@pytest.fixture
def access_token():
    def make(user_id=1, **overrides):
        payload = {"sub": str(user_id), "type": "access",
                   "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)}
        payload.update(overrides)
        return jwt.encode(payload, TEST_SECRET, algorithm="HS256")
    return make


@pytest.fixture
def logged_api(api, access_token):
    api.client.cookies.set("access_token", access_token())
    return api


@pytest.fixture
def real_api(api, postgres_database):
    connection, params = postgres_database
    with ExitStack() as stack:
        for module in vars(api.modules).values():
            cursor = stack.enter_context(connection.cursor())
            stack.enter_context(patch.object(module, "connection", connection))
            stack.enter_context(patch.object(module, "cursor", cursor))
        api.connection = connection
        api.params = params
        yield api
