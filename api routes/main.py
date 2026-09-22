from fastapi import FastAPI, APIRouter
from routers.auth.routes import router as auth_router
from routers.library.routes import router as library_router
from routers.users.routes import router as user_router
app = FastAPI()

app.include_router(auth_router)
app.include_router(library_router)
app.include_router(user_router)