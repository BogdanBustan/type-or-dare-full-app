from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.mongodb_models import UserDocument


async def init_mongodb(mongodb_url: str):
    client: AsyncIOMotorClient = AsyncIOMotorClient(mongodb_url)
    await init_beanie(database=client.user_db, document_models=[UserDocument])
