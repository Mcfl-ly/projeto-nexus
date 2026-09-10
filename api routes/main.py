from fastapi import FastAPI, APIRouter
from routers.auth.routes import router as auth_router
from routers.library.routes import router as library_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(library_router)
