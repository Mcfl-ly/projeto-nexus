from fastapi import FastAPI, HTTPException, status, Response, Request, APIRouter, Depends
import psycopg2
import datetime
import dotenv
import os
import jwt
from sqlalchemy.testing.pickleable import User
from pymongo import MongoClient
import unicodedata

# ----CONEXÕES----
connection_string = os.getenv("CONNECTION_STRING")

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

router = APIRouter(tags=["Libr"])

# ----FUNÇÕES----
def normalize_text(text: str) -> str:
    text = text.lower().strip()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )
    return text

def add_mongo():
    client = MongoClient(connection_string)
    db = client[os.getenv("DATABASE")]
    colecao = db[os.getenv("COLECAO")]
    dados = [
    {
        "title": "The Last Kingdom",
        "release_date": "2024-05-12",
        "summary": "Um RPG de ação em mundo aberto ambientado na era viking.",
        "image": "https://example.com",
        "genres": ["Action", "RPG", "Adventure"],
        "game_modes": ["Single-player", "Co-op"],
        "type": "Game"
    },
                        {
                            "title": "Space Velocity",
                            "release_date": "2025-11-20",
                            "summary": "Simulador de corrida espacial em alta velocidade com física realista.",
                            "image": "https://example.com",
                            "genres": ["Racing", "Simulation", "Sci-Fi"],
                            "game_modes": ["Single-player", "Multiplayer"],
                            "type": "Game"
                        },
    {
        "title": "Ecos do Amanhã",
        "release_date": "2023-08-15",
        "genres": ["Sci-Fi", "Drama", "Thriller"],
        "summary": "Um cientista descobre uma forma de receber mensagens do futuro, mas as consequências são catastróficas.",
        "image": "https://example.com",
        "type": "Movie"
    },
    {
        "title": "A Herança de Crimson",
        "release_date": "2026-02-05",
        "genres": ["Horror", "Mystery"],
        "summary": "Uma família herda uma mansão isolada e descobre segredos sombrios escondidos nas paredes.",
        "image": "https://example.com",
        "type": "Movie"
    },
    {
        "title": "O Império de Cinzas",
        "subtitle": "A Queda dos Três Reis",
        "authors": ["G. R. Martin", "J. R. R. Tolkien"],
        "release_date": "2021-03-30",
        "pages": 542,
        "image": "https://example.com",
        "type": "Book"
    },
    {
        "title": "Algoritmos do Pensamento",
        "subtitle": "Como a Inteligência Artificial Molda a Mente Humana",
        "authors": ["Ana Silva"],
        "release_date": "2025-09-01",
        "pages": 320,
        "image": "https://example.com",
        "type": "Book"
    }
    ]
    resultado = colecao.insert_many(dados)
    print(f"Documentos inseridos com sucesso! IDs: {resultado.inserted_ids}")
    client.close()
    return {"message": "Documentos inseridos com sucesso!"}



def search_in_mongo(title):
    # normal_title = normalize_text(title)
    client = MongoClient(connection_string)
    db = client[os.getenv("DATABASE")]
    colecao = db[os.getenv("COLECAO")]

    results = colecao.find({"title": {"$regex": title}})
    for doc in results:
        print(doc)
    return results

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

# ----ROTAS----
@router.get("/library")
async def get_library(user_id: str = Depends(get_current_user)):
    sql = "select * from userlibrary where user_id = %s"

    cursor.execute(sql, (user_id,))

    return cursor.fetchall()

@router.post("/library")
async def add_content_to_library(user: User = Depends(get_current_user)):
    insert_sql = "insert into userlibrary values (%s, %s, %s, %s, %s, %s, %s)"

@router.get("/teste")
async def teste_mongo():
    search_in_mongo("Ecos do Amanhã")


