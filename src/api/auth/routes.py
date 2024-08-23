from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.api.auth.schemas import UserCreate, UserLogin
from src.database.init_tidb import init_tidb
from src.database import TiDBHandler
from src.database.users import add_user, fetch_user_by_username, verify_password

from src.config import logger  # Import the logger


auth_router = APIRouter()


@auth_router.post("/create-new-user")
async def create_user(user: UserCreate, db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Auth] Create new user id with user information : {user}")
    try:
        # Check if the user already exists
        existing_user = fetch_user_by_username(user.username, db)
        if existing_user:
            return JSONResponse(
                status_code=400,
                content={"status": "error", "message": "Username already exists"},
            )

        # Add new user
        user_data = add_user(user.username, user.password, db)
        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "message": "User created successfully",
                "data": {"user_id": user_data["id"], "username": user_data["username"]},
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to add user",
                "error": str(e),
            },
        )


@auth_router.post("/login")
async def login_user(user: UserLogin, db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Auth] Login into the user id with user information : {user}")
    try:
        # Fetch user details from db
        db_user = fetch_user_by_username(user.username, db)

        # Validate user credentials
        if not db_user or not verify_password(user.password, db_user["password"]):
            return JSONResponse(
                status_code=401,
                content={"status": "error", "message": "Invalid username or password"},
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Login successful",
                "data": {"user_id": db_user["id"]},
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "error", "message": "Failed to login", "error": str(e)},
        )
