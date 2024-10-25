# app/api/routes.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import Select
import pandas as pd
from pydantic import ValidationError
import io

from app.models.schemas import UserData, UserList
from app.models.mongodb_models import UserDocument
from app.models.sql_models import User
from app.database.sqlite import get_session
from app.models.schemas import UserResponse

router = APIRouter()


@router.get("/user/{user_id}")
async def get_user(user_id: str, session: Session = Depends(get_session)):
    # Get from MongoDB
    mongo_user = await UserDocument.find_one({"user_id": user_id})

    # Get from SQLite using session.exec()
    statement = select(User).where(User.user_id == user_id)
    sql_user = session.exec(statement).first()

    if not mongo_user and not sql_user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "mongodb_user": mongo_user.model_dump() if mongo_user else None,
        "sqlite_user": sql_user.model_dump() if sql_user else None
    }


@router.get("/users")
async def get_all_users(session: Session = Depends(get_session)):
    # Get from MongoDB
    mongo_users = await UserDocument.find_all().to_list()

    # Get from SQLite using session.exec()
    statement = select(User)
    sql_users = session.exec(statement).all()

    return {
        "mongodb_users": [user.model_dump() for user in mongo_users],
        "sqlite_users": [user.model_dump() for user in sql_users]
    }


# MongoDB endpoints
@router.get("/mongodb/user/{user_id}", response_model=UserResponse)
async def get_mongodb_user(user_id: str):
    mongo_user = await UserDocument.find_one({"user_id": user_id})
    if not mongo_user:
        raise HTTPException(status_code=404, detail="User not found in MongoDB")
    return UserResponse(**mongo_user.model_dump())


@router.get("/mongodb/users", response_model=list[UserResponse])
async def get_all_mongodb_users():
    mongo_users = await UserDocument.find_all().to_list()
    return [UserResponse(**user.model_dump()) for user in mongo_users]


# SQLite endpoints
@router.get("/sqlite/user/{user_id}", response_model=UserResponse)
async def get_sqlite_user(user_id: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.user_id == user_id)
    sql_user = session.exec(statement).first()
    if not sql_user:
        raise HTTPException(status_code=404, detail="User not found in SQLite")
    return UserResponse(**sql_user.model_dump())


@router.get("/sqlite/users", response_model=list[UserResponse])
async def get_all_sqlite_users(session: Session = Depends(get_session)):
    statement = select(User)
    sql_users = session.exec(statement).all()
    return [UserResponse(**user.model_dump()) for user in sql_users]


@router.post("/upload/csv")
async def upload_csv(file: UploadFile = File(...), session: Session = Depends(get_session)):
    if not file:
        raise HTTPException(
            status_code=400,
            detail={"error": "No file uploaded", "message": "Please upload a CSV file"}
        )
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid filename", "message": "Please ensure the file has a name"}
        )
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid file type", "message": "File must be a CSV"}
        )

    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode('utf-8')))

        # Validate CSV data
        try:
            user_list = UserList.from_df(df)
        except (ValueError, ValidationError) as e:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": "Validation failed",
                    "message": str(e)
                }
            )

        # Save to MongoDB
        mongo_documents = [
            UserDocument(
                user_id=user.user_id,
                name=user.name,
                email=user.email,
                age=user.age
            )
            for user in user_list.users
        ]
        await UserDocument.insert_many(mongo_documents)

        # Save to SQLite
        sql_users = [
            User(
                user_id=user.user_id,
                name=user.name,
                email=user.email,
                age=user.age
            )
            for user in user_list.users
        ]
        for user in sql_users:
            session.add(user)
        session.commit()

        return {
            "message": f"Successfully processed {len(user_list.users)} records",
            "processed_count": len(user_list.users)
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Processing failed",
                "message": str(e)
            }
        )


@router.post("/user", response_model=UserData)
async def create_user(user_data: UserData, session: Session = Depends(get_session)):
    try:
        # Check if user_id or email already exists in MongoDB
        existing_mongo = await UserDocument.find_one({
            "$or": [
                {"user_id": user_data.user_id},
                {"email": user_data.email}
            ]
        })
        if existing_mongo:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Duplicate entry",
                    "message": "User ID or email already exists"
                }
            )

        # Check in SQLite
        statement = select(User).where(
            (User.user_id == user_data.user_id) |
            (User.email == user_data.email)
        )
        existing_sql = session.exec(statement).first()
        if existing_sql:
            raise HTTPException(
                status_code=409,
                detail={
                    "error": "Duplicate entry",
                    "message": "User ID or email already exists"
                }
            )

        # Save to MongoDB
        mongo_user = UserDocument(
            user_id=user_data.user_id,
            name=user_data.name,
            email=user_data.email,
            age=user_data.age
        )
        await UserDocument.insert_one(mongo_user)

        # Save to SQLite
        sql_user = User.model_validate(user_data)
        session.add(sql_user)
        session.commit()
        session.refresh(sql_user)

        return user_data

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Creation failed",
                "message": str(e)
            }
        )
