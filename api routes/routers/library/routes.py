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
from pydantic import BaseModel
import argostranslate.package
import argostranslate.translate

argostranslate.package.update_package_index()

packages = argostranslate.package.get_available_packages()

package = next(
    p for p in packages
    if p.from_code == "pt" and p.to_code == "en"
)

argostranslate.package.install_from_path(package.download())

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
connection_string = os.getenv("CONNECTION_STRING")

dotenv.load_dotenv()
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
    title: str
    type: str

class LibraryUpdate(BaseModel):
    status: str | None = None
    rating: int | None = None

class ManualContent(BaseModel):
    title: str
    type: str
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

def add_game_to_library(title, user):
    client = MongoClient(connection_string)
    db = client[os.getenv("DATABASE")]
    colecao = db[os.getenv("COLECAO")]

    insert_sql = "insert into userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    search_sql = "select * from userlibrary where user_id = %s and name = %s and content_type = %s"
    cursor.execute(search_sql, (int(user), title.title, title.type))
    exist = cursor.fetchone()
    if exist:
        client.close()
        return "jogo já existe no seu catálogo."

        # BUSCA DO MONGODB
    id_externo = search_game_in_external_api(title.title)["external_id"]


    game = colecao.find_one({
        "external_id": id_externo
    })
    if not game:
        dados = search_game_in_external_api(title.title)
        if not dados:
            client.close()
            return "Jogo não encontrado."

        insert_data = colecao.insert_one(dados)
        game_name = dados["title"]
        game_id = dados["_id"]

        cursor.execute(insert_sql,
                       (
                           int(user),
                           str(game_id),
                           game_name,
                           "Quero Jogar",
                           None,
                           datetime.date.today(),
                           id_externo,
                           title.type
                       ))
        connection.commit()
    else:
        print("bateu no else")
        game_id = game["_id"]
        game_nome = game["title"]
        external_api_id = game["external_id"]
        print(external_api_id)
        cursor.execute(insert_sql,
                        (
                        int(user),
                        str(game_id),
                        game_nome,
                        "Quero Jogar",
                        None,
                        datetime.date.today(),
                        external_api_id,
                        title.type
                        ))
        connection.commit()
        client.close()
        return "Jogo adicionado com sucesso."

def add_movie_to_library(title, user):
    client = MongoClient(connection_string)
    db = client[os.getenv("DATABASE")]
    colecao = db[os.getenv("COLECAO")]


    insert_sql = "insert into userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    search_sql = "select * from userlibrary where user_id = %s and name = %s and content_type = %s"
    cursor.execute(search_sql, (int(user), title.title, title.type))
    exist = cursor.fetchone()
    if exist:
        print("existe")
        client.close()
        return "filme já existe no seu catálogo."
# BUSCA DO MONGODB
    id_externo = search_movie_in_external_api(title.title)["external_id"]

    filme = colecao.find_one({
        "external_id": id_externo
    })
    if not filme:
        print("chegou no nao existe")
        dados = search_movie_in_external_api(title.title)
        if not dados:
            client.close()
            return "Filme não encontrado."


        insert_data = colecao.insert_one(dados)
        filme_name = dados["title"]
        filme_id = dados["_id"]

        cursor.execute(insert_sql,
                       (
                           int(user),
                           str(filme_id),
                           filme_name,
                           "Quero Assistir",
                           None,
                           datetime.date.today(),
                           id_externo,
                           title.type
                       ))
        connection.commit()

    else:
        print("bateu no else")
        filme_id = filme["_id"]
        filme_nome = filme["title"]
        external_api_id = filme["external_id"]
        print(external_api_id)
        cursor.execute(insert_sql,
                        (
                        int(user),
                        str(filme_id),
                        filme_nome,
                        "Quero Assistir",
                        None,
                        datetime.date.today(),
                        external_api_id,
                        title.type
                        ))
        connection.commit()
        client.close()
        return "Filme adicionado com sucesso."

def add_book_to_library(title, user):
    client = MongoClient(connection_string)
    db = client[os.getenv("DATABASE")]
    colecao = db[os.getenv("COLECAO")]

    insert_sql = "insert into userlibrary (user_id, content_id, name, status, rating, created_at, external_api_id, content_type) values (%s, %s, %s, %s, %s, %s, %s, %s)"
    search_sql = "select * from userlibrary where user_id = %s and name = %s and content_type = %s"
    cursor.execute(search_sql, (int(user), title.title, title.type))
    exist = cursor.fetchone()
    if exist:
        client.close()
        return "livro já existe no seu catálogo."

    # BUSCA DO MONGODB
    id_externo = search_book_in_external_api(title.title)["external_id"]

    livro = colecao.find_one({
        "external_id": id_externo
    })
    if not livro:
        dados = search_book_in_external_api(title.title)
        if not dados:
            client.close()
            return "Livro não encontrado."

        insert_data = colecao.insert_one(dados)
        livro_name = dados["title"]
        livro_id = dados["_id"]

        cursor.execute(insert_sql,
                       (
                           int(user),
                           str(livro_id),
                           livro_name,
                           "Quero Ler",
                           None,
                           datetime.date.today(),
                           id_externo,
                           title.type
                       ))
        connection.commit()

    else:
        print("bateu no else")
        livro_id = livro["_id"]
        livro_nome = livro["title"]
        external_api_id = livro["external_id"]
        print(external_api_id)
        cursor.execute(insert_sql,
                       (
                           int(user),
                           str(livro_id),
                           livro_nome,
                           "Quero Ler",
                           None,
                           datetime.date.today(),
                           external_api_id,
                           title.type
                       ))
        connection.commit()
        client.close()
        return "Livro adicionado com sucesso."

def search_in_mongo(title, tipo):
    client = MongoClient(connection_string)
    db = client[os.getenv("DATABASE")]
    colecao = db[os.getenv("COLECAO")]
    content = None
    results = colecao.find({"title": {"$regex": title}, "type": tipo})
    for doc in results:
        content = doc
    return content

#FUNÇÃO EXCLUSIVA PARA A API IGDB DA TWITCH
def get_igdb_token():

    global IGDB_TOKEN

    if IGDB_TOKEN:
        return IGDB_TOKEN

    url = "https://id.twitch.tv/oauth2/token"
    data = {
        "client_id": os.getenv("TWITCH_CLIENT_ID"),
        "client_secret": os.getenv("TWITCH_CLIENT_SECRET"),
        "grant_type": "client_credentials"
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    IGDB_TOKEN = response.json()["access_token"]
    return IGDB_TOKEN

def search_game_in_external_api(title):
    access_token = get_igdb_token()
    query = f"""
fields name, first_release_date, genres.name, cover.image_id;
search "{title}";
limit 1;
"""
    try:
        response = requests.post(
            "https://api.igdb.com/v4/games",
            headers={
                "Client-ID": os.getenv("TWITCH_CLIENT_ID"),
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            },
            data=query
        )
        if response.status_code == 200:
            results = response.json()[0]
            if results:
                timestamp = results["first_release_date"]
                date = str(datetime.datetime.fromtimestamp(timestamp)).split("T")[0].split(" ")[0]
                try:
                    genres = [genre["name"] for genre in results["genres"]]
                except:
                    genres = []

                image_url = f"https://images.igdb.com/igdb/image/upload/t_original/{results["cover"]["image_id"]}.jpg"
                return {
                    "external_id": results["id"],
                    "title": normalize_text(results["name"]),
                    "release_date": date,
                    "genres": genres,
                    "image_url": image_url,
                    "type": "game"
                }
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

def search_movie_in_external_api(title):
    tmdb_key = os.getenv("TMDB_KEY")
    url = "https://api.themoviedb.org/3/search/movie"
    main_title = normalize_text(title)
    params = {"api_key": tmdb_key,
              "query": main_title,
              "language": "pt-BR"
              }
    try:
        response = requests.get(url, params=params)

        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                primeiro_filme = results[0]

                genres = [
                    TMDB_GENRES[genre_id]
                    for genre_id in primeiro_filme.get("genre_ids", [])
                    if genre_id in TMDB_GENRES
                ]

                poster_path = primeiro_filme.get("poster_path")
                if poster_path:
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                else:
                    poster_url = None

                return {
                    "external_id": primeiro_filme["id"],
                    "title": normalize_text(primeiro_filme["title"]),
                    "original_title": normalize_text(primeiro_filme["original_title"]),
                    "overview": primeiro_filme["overview"],
                    "date": primeiro_filme["release_date"],
                    "genres": genres,
                    "poster": poster_url,
                    "type": "movie"
                }
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

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
    return argostranslate.translate.translate(
        title,
        "pt",
        "en"
    )

def search_book_in_external_api(title):
    global response
    url = "https://openlibrary.org/search.json"
    normal_title = normalize_text(title)
    texto_traduzido = translate_title(normal_title)
    params = {
        "title": normal_title,
        "fields": "key,subject,title,author_name,first_publish_year,cover_i",
        "limit": 1,
        "lang": "pt"
    }
    try:
        params = {
            "title": normal_title,
            "fields": "key,subject,title,author_name,first_publish_year,cover_i",
            "limit": 1,
            "lang": "pt"
        }
        try:
            response = requests.get(url, params=params)
        except:
            params = {
                "title": normalize_text(texto_traduzido),
                "fields": "key,subject,title,author_name,first_publish_year,cover_i",
                "limit": 1,
                "lang": "pt"
            }
        if response.status_code == 200:
            results = response.json()["docs"][0]
            subjects = results.get("subject", [])
            genres = extract_genres(subjects)
            image_url = f"https://covers.openlibrary.org/b/id/{results["cover_i"]}-L.jpg"
            return {
                "external_id": results["key"],
                "title": normalize_text(results["title"]),
                "author_name": results["author_name"],
                "release_date": results["first_publish_year"],
                "genres": genres,
                "image_url": image_url,
                "type": "book"
            }
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

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
    print(movie)
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

def add_manual_game_to_library(dados, user):
    client = MongoClient(connection_string)
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

def add_manual_book_to_library(dados, user):
    client = MongoClient(connection_string)
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
# ----ROTAS----
@router.get("/library")
async def get_library(user_id: str = Depends(get_current_user)):

    sql = "select * from userlibrary where user_id = %s"

    cursor.execute(sql, (user_id,))

    return cursor.fetchall()

@router.post("/library")
async def add_content(title: ContentRequest, user = Depends(get_current_user)):
    if title.type == "movie":
        try:
            return add_movie_to_library(title, user)
        except psycopg2.errors.UniqueViolation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
            )
    elif title.type == "game":
        try:
            return add_game_to_library(title, user)
        except psycopg2.errors.UniqueViolation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
            )
    elif title.type == "book":
        try:
            return add_book_to_library(title, user)
        except psycopg2.errors.UniqueViolation:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
            )

@router.patch("/library/{id}")
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
async def add_manual_content(dados: ManualContent, user = Depends(get_current_user)):
    # print(dados)
    if dados.type == "movie":
        return add_manual_movie_to_library(dados, user)
    elif dados.type == "game":
        return add_manual_game_to_library(dados, user)
    else:
        return add_manual_book_to_library(dados, user)
