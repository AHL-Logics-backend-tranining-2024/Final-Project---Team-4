from fastapi import FastAPI
from app.api import api_router
from contextlib import asynccontextmanager
from app.database import close_db_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()  
    try:
        yield
    finally:
        await close_db_connection() 

app = FastAPI(lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")
