from catalog import close_catalog
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from settings import CORS_ORIGINS
from routers.auth.routes import router as auth_router
from routers.library.routes import router as library_router
from routers.users.routes import router as user_router

@asynccontextmanager
async def lifespan(app):
    yield
    close_catalog()

app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"])
app.include_router(auth_router)
app.include_router(library_router)
app.include_router(user_router)

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

# The production container serves React and the API from the same HTTPS origin.
# Explicit client routes avoid turning unknown API paths into HTML responses.
dist = Path(__file__).resolve().parents[1] / "front" / "nexus" / "dist"
if dist.is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")
    @app.get("/", include_in_schema=False)
    @app.get("/login", include_in_schema=False)
    @app.get("/cadastro", include_in_schema=False)
    @app.get("/filmes", include_in_schema=False)
    @app.get("/jogos", include_in_schema=False)
    @app.get("/livros", include_in_schema=False)
    @app.get("/perfil", include_in_schema=False)
    async def frontend():
        return FileResponse(dist / "index.html")

    @app.get("/favicon.svg", include_in_schema=False)
    async def favicon():
        return FileResponse(dist / "favicon.svg")
