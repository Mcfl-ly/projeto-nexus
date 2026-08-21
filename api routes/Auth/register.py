from fastapi import FastAPI
from pydantic import BaseModel, EmailStr, ValidationError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

pswdHasher = PasswordHasher()
app = FastAPI()

class Register(BaseModel):
    email: EmailStr
    password: str
    name: str


@app.post("/register")
async def register(dados: Register):
    hashed = pswdHasher.hash(dados.password)
    print(hashed)
    try:
        pswdHasher.verify(hashed, dados.password)
        print("ta engual")
    except VerifyMismatchError:
        print("verification error")
    return dados