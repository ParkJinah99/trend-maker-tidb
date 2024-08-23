from fastapi import HTTPException

from src.database.tidb_handler import TiDBHandler
from src.database.sql_queries import INSERT_USER_QUERY, SELECT_USER_BY_USERNAME_QUERY

from src.config import logger  # Import the logger


def add_user(username: str, password: str, db: TiDBHandler):
    logger.info(
        f"[TIDB] Add new user with username and password: {username}, {password}"
    )
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(INSERT_USER_QUERY, (username, password))
            db.connection.commit()
            user_id = cursor.lastrowid
            return {"id": user_id, "username": username}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def fetch_user_by_username(username: str, db: TiDBHandler):
    logger.info(f"[TIDB] Retreive user information with username: {username}")
    try:
        # Execute the query using execute_query_as_dict
        result_list = db.execute_query_as_dict(
            SELECT_USER_BY_USERNAME_QUERY, params=(username,)
        )

        # Check if any result was returned
        if result_list:
            return result_list[
                0
            ]  # Return the first (and likely only) result as a dictionary
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def verify_password(password: str, db_password: str):
    logger.info(f"[TIDB] Verify password")
    return password == db_password
