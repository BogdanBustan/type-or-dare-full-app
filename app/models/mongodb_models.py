from beanie import Document
from datetime import datetime


class UserDocument(Document):
    user_id: str
    name: str
    email: str
    age: int
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"
