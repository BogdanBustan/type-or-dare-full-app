from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing_extensions import Annotated
import pandas as pd


class UserData(BaseModel):
    user_id: Annotated[str, Field(description="Unique identifier for the user", pattern=r'^USR\d{3}$')]
    name: Annotated[str, Field(min_length=2, max_length=50)]
    email: Annotated[EmailStr, Field(description="Email address of the user")]
    age: Annotated[int, Field(ge=0, le=120)]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('name')
    @classmethod
    def name_must_be_alphabetic(cls, v: str) -> str:
        if not all(c.isalpha() or c.isspace() for c in v):
            raise ValueError('Name must contain only letters and spaces')
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "USR001",
                    "name": "John Doe",
                    "email": "john.doe@example.com",
                    "age": 30
                }
            ]
        }
    }


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    age: int
    created_at: datetime


class UserList(BaseModel):
    users: List[UserData]

    @classmethod
    def from_df(cls, df: pd.DataFrame) -> 'UserList':
        users_data = []
        errors = []

        for index, row in df.iterrows():
            try:
                user = UserData(
                    user_id=row['user_id'],
                    name=row['name'],
                    email=row['email'],
                    age=row['age']
                )
                users_data.append(user)
            except Exception as e:
                errors.append(f"Row {index + 1}: {str(e)}")

        if errors:
            raise ValueError("\n".join(errors))

        return cls(users=users_data)