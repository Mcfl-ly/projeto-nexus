from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, ValidationError, Field
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import psycopg2
import datetime

connection = psycopg2.connect(
    dbname="content_trackerDB",
    host="localhost",
    port="5432",
    user="postgres",
    password="dekudeku7",
)

cursor = connection.cursor()

pswdHasher = PasswordHasher()
app = FastAPI()

class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str


@app.post("/register")
async def register(dados: Register):
    hashed = pswdHasher.hash(dados.password)
    sql = "INSERT INTO users (email, password, name, created_at) VALUES (%s, %s, %s, %s)"

    try:
        cursor.execute(sql, (dados.email, hashed, dados.name, datetime.date.today()))
        connection.commit()

    except VerifyMismatchError:
        print("verification error")
    return dados