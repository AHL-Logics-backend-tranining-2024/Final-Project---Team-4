from fastapi import FastAPI
from app.api import api_router
from contextlib import asynccontextmanager
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")
