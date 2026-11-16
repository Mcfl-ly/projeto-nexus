from contextlib import nullcontext
from database import RequestConnection, request_scope
from functools import wraps

import psycopg2
from fastapi import HTTPException
from pymongo.errors import PyMongoError


def handle_database_errors(get_connection):
    """Desfaz transacoes que falharam sem expor detalhes internos ao cliente."""
    def decorate(handler):
        @wraps(handler)
        async def wrapped(*args, **kwargs):
            try:
                scope = request_scope() if isinstance(get_connection(), RequestConnection) else nullcontext()
                with scope:
                    return await handler(*args, **kwargs)
            except (psycopg2.Error, PyMongoError) as error:
                try:
                    get_connection().rollback()
                except psycopg2.Error:
                    # Uma conexao encerrada pode falhar tambem no rollback.
                    pass
                if isinstance(error, psycopg2.errors.UniqueViolation):
                    raise HTTPException(status_code=409, detail="Registro já existe.") from None
                raise HTTPException(status_code=503, detail="Serviço de dados indisponível.") from None
        return wrapped
    return decorate
