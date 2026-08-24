from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, EmailStr, ValidationError, Field
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
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
app = FastAPI()



# ----FUNÇÕES----
def create_access_token(user_id):
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)

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

@app.post("/register")
async def register(dados: Register):
    hashed = pswdHasher.hash(dados.password)
    sql = "INSERT INTO users (email, password, name, created_at) VALUES (%s, %s, %s, %s)"

    try:
        cursor.execute(sql, (dados.email, hashed, dados.name, datetime.date.today()))
        connection.commit()

    except VerifyMismatchError:
        print("verification error")



@app.post("/login")
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
        hashed_token = pswdHasher.hash(access_token)

        cursor.execute(token_sql, (result[0], hashed_token, expires_at, "false", created_at))
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
            max_age=60 * 60 * 24 * 7
        )
        return {
            "status": "sucesso",
            "mensagem": "Senha correta."
        }
    except Exception:
        raise erro_autenticacao



