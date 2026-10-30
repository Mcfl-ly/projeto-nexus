from fastapi import FastAPI, APIRouter
from routers.auth.routes import router as auth_router
from routers.library.routes import router as library_router
from routers.users.routes import router as user_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth_router)
app.include_router(library_router)
app.include_router(user_router)