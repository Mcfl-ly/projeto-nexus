from fastapi import FastAPI, HTTPException, status, Response, Request, APIRouter
from pydantic import BaseModel, EmailStr, ValidationError, Field
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
import psycopg2
import datetime
import dotenv
import os
import jwt

# ----CONEXÕES----
dotenv.load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

connection = psycopg2.connect(
    dbname=os.getenv("DBNAME"),
    host=os.getenv("HOST"),
    port=os.getenv("PORT"),
    user=os.getenv("USER"),
    password=os.getenv("PASSWORD"),
)

cursor = connection.cursor()

pswdHasher = PasswordHasher()

router = APIRouter(tags=["Auth"])


# ----FUNÇÕES----
def create_access_token(user_id):
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

    payload = {
        "exp": expires,
        "type": "access",
        "sub": str(user_id)
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm
    )

def create_refresh_token(user_id):
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)

    payload = {
        "exp": expires,
        "type": "refresh",
        "sub": str(user_id)
    }

    return jwt.encode(
        payload,
        secret_key,
        algorithm=algorithm
    )


# ---CLASSES----
class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str

class Login(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


# ----ROTAS----
@router.post("/register")
async def register(dados: Register):
    hashed = pswdHasher.hash(dados.password)
    sql = "INSERT INTO users (email, password, name, created_at) VALUES (%s, %s, %s, %s)"

    try:
        cursor.execute(sql, (dados.email, hashed, dados.name, datetime.date.today()))
        connection.commit()

    except VerifyMismatchError:
        print("verification error")


@router.post("/login")
async def login(dados: Login, response: Response):
    token_sql = "INSERT INTO refreshtoken (user_id, token, expires_at, revoked, created_at) VALUES (%s, %s, %s, %s, %s)"

    sql = "SELECT * FROM users WHERE email = %s"
    cursor.execute(sql, (dados.email,))
    result = cursor.fetchone()
    erro_autenticacao = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="E-mail ou senha incorretos.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not result:
        raise erro_autenticacao

    try:
        pswdHasher.verify(result[2], dados.password)
        access_token = create_access_token(result[0])
        refresh_token = create_refresh_token(result[0])
        created_at = datetime.date.today()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
        hashed_token = pswdHasher.hash(refresh_token)

        cursor.execute(token_sql, (result[0], hashed_token, expires_at, False, created_at))
        connection.commit()

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 15
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=60 * 60 * 24 * 30
        )
        return {
            "status": "sucesso",
            "mensagem": "Senha correta."
        }
    except Exception:
        raise erro_autenticacao



@router.post("/logout")
async def logout(response: Response, request: Request):
    sql_update = "UPDATE refreshtoken SET revoked=true WHERE id = %s"
    sql_select = "SELECT id, token FROM refreshtoken WHERE revoked = false"
    cursor.execute(sql_select)
    tokens = cursor.fetchall()
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        for token in tokens:
            try:
                print("iniciar aq")
                if pswdHasher.verify(token[1], refresh_token):
                    cursor.execute(sql_update, (token[0],))
                    connection.commit()
                    break
            except VerifyMismatchError:
                print("token incorreto")
                continue
            except InvalidHashError:
                print("hash incorreto")
                continue
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="lax"
    )
    return {"message": "Logout realizado com sucesso."}


@router.post("/refresh")
async def refresh(response: Response, request: Request):
    refresh_token = request.cookies.get("refresh_token")
    sql_check = "SELECT * FROM refreshtoken WHERE revoked = false"
    sql_rotate_token = "UPDATE refreshtoken SET revoked=true WHERE id = %s"
    sql_add_new_refresh_token = "INSERT INTO refreshtoken (user_id, token, expires_at, revoked, created_at) VALUES (%s, %s, %s, %s, %s)"
    cursor.execute(sql_check)
    tokens = cursor.fetchall()
    for token in tokens:
        try:
            valid = pswdHasher.verify(token[2], refresh_token)
        except:
            continue
        if valid:
            print("1 - refresh válido")
            if not datetime.date.today() >= token[3]:
                print("2 - refresh não expirado")

                created_at = datetime.datetime.now(datetime.timezone.utc)
                expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30)
                print("3 - criando tokens")

                new_access_token = create_access_token(token[1])
                new_refresh_token = create_refresh_token(token[1])
                print("NOVO REFRESH:", new_refresh_token)

                hashed_new_refresh_token = pswdHasher.hash(new_refresh_token)
                print("4 - hash criado")

                cursor.execute(sql_rotate_token, (token[0],))
                print("5 - token antigo revogado")

                cursor.execute(sql_add_new_refresh_token, (token[1], hashed_new_refresh_token, expires_at, False, created_at))
                connection.commit()
                print("6 - novo refresh inserido")

                response.set_cookie(
                    key="access_token",
                    value=new_access_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=60 * 15
                )
                response.set_cookie(
                    key="refresh_token",
                    value=new_refresh_token,
                    httponly=True,
                    secure=True,
                    samesite="lax",
                    max_age=60 * 60 * 24 * 30
                )
                print("7 - cookies atualizados")
                return {"message": "Access token renovado"}


    raise HTTPException(status_code=401, detail="Refresh token inválido.")