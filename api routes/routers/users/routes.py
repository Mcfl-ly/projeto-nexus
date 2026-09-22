from fastapi import FastAPI, HTTPException, status, Response, Request, APIRouter, Depends
import psycopg2
import datetime
import dotenv
import os
import jwt
from pymongo import MongoClient
import unicodedata
import requests
from pydantic import BaseModel, Field
from argon2 import PasswordHasher

pswdHasher = PasswordHasher()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

class ContentRequest(BaseModel):
    title: str
    type: str

class UserUpdate(BaseModel):
    username: str | None = None

class PasswordUpdate(BaseModel):
    password: str = Field(min_length=8, max_length=64)

connection = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
)

cursor = connection.cursor()

router = APIRouter(tags=["User"])

def get_current_user(request: Request):
    access_token = request.cookies.get("access_token")

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não autenticado"
        )

    try:
        payload = jwt.decode(
            access_token,
            secret_key,
            algorithms=[algorithm],
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expirado"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token inválido"
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
    return user_id


@router.get("/users/me")
async def users_me(current_user = Depends(get_current_user)):
    user_sql = "SELECT * FROM users WHERE id = %s"
    content_sql = "SELECT * FROM userlibrary WHERE user_id = %s"
    cursor.execute(user_sql, (current_user,))
    user = cursor.fetchone()
    cursor.execute(content_sql, (current_user,))
    content = cursor.fetchall()
    final_content = []
    for item in content:
        final_content.append(
            {
                "id": item[0],
                "mongo_id": item[2],
                "name": item[3],
                "status": item[4],
                "rating": item[5],
                "type": item[7],
            }
        )
    returned_user = {
        "email": user[1],
        "username": user[3],
        "created_at": user[4],
        "content": final_content,
    }
    return returned_user


#ALTERAR NOME DE USUÁRIO
@router.patch("/users/me")
async def update_username(data: UserUpdate, user_id: str = Depends(get_current_user)):
    cursor.execute(
        """
        SELECT name
        FROM users
        WHERE id = %s
        """,
        (int(user_id),)
    )

    library = cursor.fetchone()
    if library is None:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado."
    )

    cursor.execute(
        """
        UPDATE users
        SET name = %s
        WHERE id = %s
        """,
        (
            data.username,
            int(user_id)
        )
    )
    connection.commit()
    return {
        "name": data.username
    }

#ALTERAR SENHA
@router.patch("/users/me/password")
async def update_password(new_pswd: PasswordUpdate, user = Depends(get_current_user)):
    password = new_pswd.password
    hashed_pswd = pswdHasher.hash(password)

    cursor.execute(
        """
        UPDATE users
        SET password = %s
        WHERE id = %s
        """,
        (
            hashed_pswd,
            int(user)
        )
    )
    connection.commit()
    return {
        "êxito": "Senha alterada com sucesso!"
    }

@router.delete("/users/me/delete")
async def delete_user(current_user = Depends(get_current_user)):
    sql_1 = "DELETE FROM refreshtoken WHERE user_id = %s"
    sql_2 = "DELETE FROM userlibrary WHERE user_id = %s"
    sql_3 = "DELETE FROM users WHERE id = %s"

    cursor.execute(sql_1, (int(current_user),))
    cursor.execute(sql_2, (int(current_user),))
    cursor.execute(sql_3, (int(current_user),))
    connection.commit()
    return {
        "êxito": "perfil excluido com sucesso!."
    }