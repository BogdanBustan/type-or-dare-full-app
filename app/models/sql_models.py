from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str
    email: str
    age: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
