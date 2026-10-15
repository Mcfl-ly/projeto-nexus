from typing import Literal
import json
from routers.db_errors import handle_database_errors
from deep_translator import GoogleTranslator
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
# ----CONEXÕES----
GENRE_MAP = {
    # Inglês
    "fantasy": "Fantasia",
    "science fiction": "Ficção científica",
    "fiction": "Ficção",
    "horror": "Terror",
    "romance": "Romance",
    "mystery": "Mistério",
    "thriller": "Suspense",
    "adventure": "Aventura",
    "historical fiction": "Ficção histórica",
    "historical": "Histórico",
    "drama": "Drama",
    "comedy": "Comédia",
    "crime": "Crime",
    "detective fiction": "Policial",
    "biography": "Biografia",
    "autobiography": "Autobiografia",
    "poetry": "Poesia",
    "philosophy": "Filosofia",
    "religion": "Religião",
    "history": "História",
    "psychology": "Psicologia",

    # Português
    "fantasia": "Fantasia",
    "ficção científica": "Ficção científica",
    "ficção": "Ficção",
    "terror": "Terror",
    "romance": "Romance",
    "mistério": "Mistério",
    "suspense": "Suspense",
    "aventura": "Aventura",
    "drama": "Drama",
    "comédia": "Comédia",
    "crime": "Crime",
    "poesia": "Poesia",
    "biografia": "Biografia",
    "autobiografia": "Autobiografia",
    "história": "História",
}
dotenv.load_dotenv()
connection_string = os.getenv("CONNECTION_STRING")
IGDB_TOKEN = None
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

class ContentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    type: Literal["movie", "game", "book"]

class LibraryUpdate(BaseModel):
    status: str | None = None
    rating: int | None = None

class ManualContent(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    type: Literal["movie", "game", "book"]
    author: list | None = None
    release_date: str | None = None
    genres: list | None = None
    img_url: str | None = None


TMDB_GENRES = {
    28: "Ação",
    12: "Aventura",
    16: "Animação",
    35: "Comédia",
    80: "Crime",
    99: "Documentário",
    18: "Drama",
    10751: "Família",
    14: "Fantasia",
    36: "História",
    27: "Terror",
    10402: "Música",
    9648: "Mistério",
    10749: "Romance",
    878: "Ficção científica",
    10770: "Cinema TV",
    53: "Thriller",
    10752: "Guerra",
    37: "Faroeste"
}
# ----FUNÇÕES----
def normalize_text(text: str) -> str:
    text = text.lower().strip()

    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        char for char in text
        if not unicodedata.combining(char)
    )
    return text

def _add_catalog_content(title, user, search, label, initial_status):
    cursor.execute(
        "SELECT id FROM userlibrary WHERE user_id = %s AND name = %s AND content_type = %s",
        (int(user), title.title, title.type),
    )
    if cursor.fetchone():
        return f"{label.lower()} já existe no seu catálogo."
    dados = search(title.title)
    if not dados:
        raise HTTPException(status_code=404, detail=f"{label} não encontrado.")
    client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
    try:
        collection = client[os.getenv("DATABASE")][os.getenv("COLECAO")]
        # IDs numericos podem coincidir entre provedores diferentes.
        content = collection.find_one({"external_id": dados["external_id"], "type": title.type})
        if content is None:
            result = collection.insert_one(dados)
            content = dados
            content.setdefault("_id", result.inserted_id)
        cursor.execute(
            "INSERT INTO userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (int(user), str(content["_id"]), content["title"], initial_status, None,
             datetime.date.today(), str(dados["external_id"]), title.type),
        )
        connection.commit()
        return f"{label} adicionado com sucesso."
    finally:
        client.close()


def _external_json(request, url, **kwargs):
    try:
        response = request(url, timeout=(3.05, 10), **kwargs)
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Serviço externo indisponível.")
        return response.json()
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Tempo limite do serviço externo excedido.") from None
    except (requests.RequestException, ValueError):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.") from None


def add_game_to_library(title, user):
    return _add_catalog_content(title, user, search_game_in_external_api, "Jogo", "Quero Jogar")

def add_movie_to_library(title, user):
    return _add_catalog_content(title, user, search_movie_in_external_api, "Filme", "Quero Assistir")

def add_book_to_library(title, user):
    return _add_catalog_content(title, user, search_book_in_external_api, "Livro", "Quero Ler")

def search_in_mongo(title, tipo):
    client = MongoClient(connection_string)
    try:
        db = client[os.getenv("DATABASE")]
        colecao = db[os.getenv("COLECAO")]
        content = None
        results = colecao.find({"title": {"$regex": title}, "type": tipo})
        for doc in results:
            content = doc
        return content
    finally:
        client.close()

#FUNÇÃO EXCLUSIVA PARA A API IGDB DA TWITCH
def get_igdb_token():
    global IGDB_TOKEN
    if IGDB_TOKEN:
        return IGDB_TOKEN
    data = _external_json(requests.post, "https://id.twitch.tv/oauth2/token", data={
        "client_id": os.getenv("TWITCH_CLIENT_ID"),
        "client_secret": os.getenv("TWITCH_CLIENT_SECRET"),
        "grant_type": "client_credentials",
    })
    if not isinstance(data, dict) or not isinstance(data.get("access_token"), str):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.")
    IGDB_TOKEN = data["access_token"]
    return IGDB_TOKEN

def search_game_in_external_api(title):
    access_token = get_igdb_token()
    query = ('fields name, first_release_date, genres.name, cover.image_id; '
             f'search {json.dumps(title)}; limit 1;')
    results = _external_json(requests.post, "https://api.igdb.com/v4/games", headers={
        "Client-ID": os.getenv("TWITCH_CLIENT_ID"), "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }, data=query)
    if not isinstance(results, list):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.")
    if not results:
        raise HTTPException(status_code=404, detail="Jogo não encontrado.")
    try:
        game = results[0]
        timestamp = game.get("first_release_date")
        release = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).date().isoformat() if timestamp is not None else None
        cover = (game.get("cover") or {}).get("image_id")
        return {
            "external_id": game["id"], "title": normalize_text(game["name"]),
            "release_date": release, "genres": [genre["name"] for genre in (game.get("genres") or [])],
            "image_url": f"https://images.igdb.com/igdb/image/upload/t_original/{cover}.jpg" if cover else None,
            "type": "game",
        }
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError, OSError):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.") from None

def search_movie_in_external_api(title):
    data = _external_json(requests.get, "https://api.themoviedb.org/3/search/movie", params={
        "api_key": os.getenv("TMDB_KEY"), "query": normalize_text(title), "language": "pt-BR",
    })
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.")
    if not data["results"]:
        raise HTTPException(status_code=404, detail="Filme não encontrado.")
    try:
        movie = data["results"][0]
        poster = movie.get("poster_path")
        return {
            "external_id": movie["id"], "title": normalize_text(movie["title"]),
            "original_title": normalize_text(movie.get("original_title") or movie["title"]),
            "overview": movie.get("overview", ""), "date": movie.get("release_date"),
            "genres": [TMDB_GENRES[g] for g in (movie.get("genre_ids") or []) if g in TMDB_GENRES],
            "poster": f"https://image.tmdb.org/t/p/w500{poster}" if poster else None,
            "type": "movie",
        }
    except (KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.") from None

#FUNÇÃO EXCLUSIVA PARA A API OPEN LIBRARY
def extract_genres(subjects):
    genres = []

    for subject in subjects:
        subject_normalized = subject.strip().lower()

        if subject_normalized in GENRE_MAP:
            genre = GENRE_MAP[subject_normalized]

            if genre not in genres:
                genres.append(genre)

    return genres

def translate_title(title):
    # Traducao e opcional. Modelos devem ser instalados fora da inicializacao
    # da API; nunca baixar/instalar pacotes ao importar as rotas.
    try:
        import argostranslate.translate
        return argostranslate.translate.translate(title, "pt", "en")
    except Exception:
        return title

def search_book_in_external_api(title):
    normal_title = normalize_text(title)
    params = {"title": normal_title, "fields": "key,subject,title,author_name,first_publish_year,cover_i", "limit": 1, "lang": "pt"}
    data = _external_json(requests.get, "https://openlibrary.org/search.json", params=params)
    if not isinstance(data, dict) or not isinstance(data.get("docs"), list):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.")
    if not data["docs"]:
        translated = normalize_text(translate_title(normal_title))
        if translated != normal_title:
            data = _external_json(requests.get, "https://openlibrary.org/search.json", params={**params, "title": translated})
        if not isinstance(data, dict) or not isinstance(data.get("docs"), list):
            raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.")
        if not data["docs"]:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
    try:
        book = data["docs"][0]
        cover = book.get("cover_i")
        return {
            "external_id": book["key"], "title": normalize_text(book["title"]),
            "author_name": book.get("author_name") or [], "release_date": book.get("first_publish_year"),
            "genres": extract_genres(book.get("subject") or []),
            "image_url": f"https://covers.openlibrary.org/b/id/{cover}-L.jpg" if cover else None,
            "type": "book",
        }
    except (KeyError, TypeError, AttributeError):
        raise HTTPException(status_code=502, detail="Resposta inválida do serviço externo.") from None

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


    # title: str
    # type: str
    # author: list | None = None
    # release_date: str | None = None
    # genres: list | None = None
    # img_url: str | None = None

def add_manual_movie_to_library(dados, user):
    client = MongoClient(connection_string)
    try:
        db = client[os.getenv("DATABASE")]
        colecao = db[os.getenv("COLECAO")]
    
        data_to_insert = {
            "title": dados.title,
            "author": dados.author,
            "release_date": dados.release_date,
            "genres": dados.genres,
            "img_url": dados.img_url,
            "type": dados.type,
        }
        colecao.insert_one(data_to_insert)
        movie = colecao.find_one({"title": dados.title})
        insert_sql = "insert into userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    
        cursor.execute(insert_sql, (
            user,
            str(movie["_id"]),
            movie["title"],
            "Quero Assistir",
            None,
            datetime.date.today(),
            None,
            "movie"
    
        ))
        connection.commit()
    finally:
        client.close()

def add_manual_game_to_library(dados, user):
    client = MongoClient(connection_string)
    try:
        db = client[os.getenv("DATABASE")]
        colecao = db[os.getenv("COLECAO")]
    
        data_to_insert = {
            "title": dados.title,
            "release_date": dados.release_date,
            "genres": dados.genres,
            "img_url": dados.img_url,
            "type": dados.type,
        }
        colecao.insert_one(data_to_insert)
        game = colecao.find_one({"title": dados.title})
        insert_sql = "insert into userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    
        cursor.execute(insert_sql, (
            user,
            str(game["_id"]),
            game["title"],
            "Quero Jogar",
            None,
            datetime.date.today(),
            None,
            "game"
    
        ))
        connection.commit()
    finally:
        client.close()

def add_manual_book_to_library(dados, user):
    client = MongoClient(connection_string)
    try:
        db = client[os.getenv("DATABASE")]
        colecao = db[os.getenv("COLECAO")]
    
        data_to_insert = {
            "title": dados.title,
            "author": dados.author,
            "release_date": dados.release_date,
            "genres": dados.genres,
            "img_url": dados.img_url,
            "type": dados.type,
        }
        colecao.insert_one(data_to_insert)
        book = colecao.find_one({"title": dados.title})
    
        insert_sql = "insert into userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    
        cursor.execute(insert_sql, (
            user,
            str(book["_id"]),
            book["title"],
            "Quero Ler",
            None,
            datetime.date.today(),
            None,
            "book"
    
        ))
        connection.commit()
    finally:
        client.close()
# ----ROTAS----
@router.get("/library")
@handle_database_errors(lambda: connection)
async def get_library(user_id: str = Depends(get_current_user)):

    sql = "select * from userlibrary where user_id = %s"

    cursor.execute(sql, (user_id,))

    return cursor.fetchall()

@router.post("/library")
@handle_database_errors(lambda: connection)
async def add_content(title: ContentRequest, user = Depends(get_current_user)):
    handlers = {"movie": add_movie_to_library, "game": add_game_to_library, "book": add_book_to_library}
    return handlers[title.type](title, user)

@router.patch("/library/{id}")
@handle_database_errors(lambda: connection)
async def update_library(
    id: int,
    data: LibraryUpdate,
    user_id: str = Depends(get_current_user)):
    cursor.execute(
        """
        SELECT status, rating
        FROM userlibrary
        WHERE user_id = %s
        AND id = %s
        """,
        (user_id, id)
    )
    library = cursor.fetchone()
    if library is None:
        raise HTTPException(
            status_code=404,
            detail="Conteúdo não encontrado"
    )
    current_status, current_rating = library

    new_status = (
        data.status
        if data.status is not None
        else current_status
    )
    new_rating = (
        data.rating
        if data.rating is not None
        else current_rating
    )
    cursor.execute(
        """
        UPDATE userlibrary
        SET status = %s,
            rating = %s
        WHERE user_id = %s
        AND id = %s
        """,
        (
            new_status,
            new_rating,
            user_id,
            id
        )
    )
    connection.commit()
    return {
        "status": new_status,
        "rating": new_rating,
    }

@router.delete("/library/{id}")
@handle_database_errors(lambda: connection)
async def delete_library(
        id: int,
        user_id: str = Depends(get_current_user)
):
    cursor.execute(
        """
                DELETE
                FROM userlibrary
                WHERE user_id = %s
                AND id = %s
                """,
        (user_id, id)
    )
    connection.commit()

@router.post("/library/manual")
@handle_database_errors(lambda: connection)
async def add_manual_content(dados: ManualContent, user = Depends(get_current_user)):
    # print(dados)
    if dados.type == "movie":
        return add_manual_movie_to_library(dados, user)
    elif dados.type == "game":
        return add_manual_game_to_library(dados, user)
    else:
        return add_manual_book_to_library(dados, user)
