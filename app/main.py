from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.api.routes import router
from app.database.mongodb import init_mongodb
from app.database.sqlite import init_db
import os


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    await init_mongodb(mongodb_url)
    init_db()
    yield


app = FastAPI(title="Dual Database FastAPI Example", lifespan=lifespan)
app.include_router(router, prefix="/api")
