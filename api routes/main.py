from fastapi import FastAPI, APIRouter
from routers.auth.routes import router as auth_router

app = FastAPI()

app.include_router(auth_router)

