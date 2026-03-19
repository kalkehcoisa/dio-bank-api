from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import init_db
from src.routers import users, transactions


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="API Bancária",
    description=(
        "API RESTful assíncrona para gerenciamento de operações bancárias. "
        "Autentique-se via `/auth/token` e use o token Bearer nos endpoints protegidos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(transactions.router)


@app.get("/", tags=["Health"], summary="Health check")
async def root():
    return {"status": "ok", "message": "API Bancária no ar"}
