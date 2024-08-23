from fastapi import HTTPException
from typing import List, Dict
from src.database.tidb_handler import TiDBHandler
from src.database.sql_queries import (
    INSERT_THREAD_QUERY,
    SELECT_USER_THREADS_QUERY,
    SELECT_THREAD_METADATA_QUERY,
    DELETE_THREAD_BY_ID_QUERY,
    INSERT_THREAD_SNAPSHOT_QUERY,
    UPDATE_THREAD_NAME_QUERY,
    DELETE_SNAPSHOT_QUERY,
    SELECT_THREAD_SNAPSHOT_QUERY,
    SELECT_SNAPSHOT_QUERY,
    DELETE_SNAPSHOT_STRATEGIES_QUERY,
    DELETE_SNAPSHOT_STATISTICS_QUERY,
)
import json
import datetime

from src.config import logger  # Import the logger


def create_thread(
    user_id: int,
    name: str,
    query: str,
    country: str,
    query_embeddings: List[float],
    keywords: List[str],
    keywords_embeddings: List[float],
    db: TiDBHandler,
):
    logger.info(f"[TIDB] Create thread with user and keyword information: {user_id}")
    try:
        query_embeddings = json.dumps(query_embeddings)
        keywords = json.dumps(keywords)
        keywords_embeddings = json.dumps(keywords_embeddings)
        with db.connection.cursor() as cursor:
            cursor.execute(
                INSERT_THREAD_QUERY,
                (
                    user_id,
                    name,
                    query,
                    country,
                    query_embeddings,
                    keywords,
                    keywords_embeddings,
                ),
            )
            db.connection.commit()
            thread_id = cursor.lastrowid
            return thread_id

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def fetch_user_threads(user_id: int, db: TiDBHandler):
    logger.info(f"[TIDB] Retrieve thread with user id: {user_id}")
    try:
        # Inject the user_id directly into the SQL query
        threads_list = db.execute_query_as_dict(
            SELECT_USER_THREADS_QUERY, params=(user_id,)
        )
        if not threads_list:
            return []

        # Convert "created_at" to string format if present
        for item in threads_list:
            if "created_at" in item:
                item["created_at"] = str(item["created_at"])
        return threads_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_thread_name(thread_id: int, new_name: str, db: TiDBHandler):
    logger.info(f"[TIDB] Update new name for the thread : {thread_id}, {new_name}")
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(UPDATE_THREAD_NAME_QUERY, (new_name, thread_id))
            db.connection.commit()

            if cursor.rowcount == 0:
                return None

            return {"id": thread_id, "name": new_name}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def fetch_thread_metadata(thread_id: int, db: TiDBHandler):
    try:
        thread_metadata_list = db.execute_query_as_dict(
            SELECT_THREAD_METADATA_QUERY, params=(thread_id,)
        )

        if not thread_metadata_list:
            return None

        thread_metadata = thread_metadata_list[0]
        thread_metadata["created_at"] = str(thread_metadata["created_at"])
        return thread_metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def remove_thread_by_id(thread_id: int, db: TiDBHandler):
    logger.info(f"[TIDB] Remove thread with thread id: {thread_id}")
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(DELETE_THREAD_BY_ID_QUERY, (thread_id,))
            db.connection.commit()

            return cursor.rowcount > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def create_thread_snapshot(thread_metadata: Dict, db: TiDBHandler):
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(
                INSERT_THREAD_SNAPSHOT_QUERY,
                (
                    thread_metadata["id"],
                    thread_metadata["name"],
                    thread_metadata["created_at"].split()[0],
                ),
            )
            cursor.execute("SELECT LAST_INSERT_ID();")
            snapshot_id = cursor.fetchone()[0]

        # Fetch the newly created snapshot
        result_list = db.execute_query_as_dict(
            SELECT_SNAPSHOT_QUERY, params=(snapshot_id,)
        )

        if not result_list:
            raise Exception("Snapshot not found after insertion.")

        result_dict = result_list[0]

        # Convert timestamp_from and timestamp_to if they are datetime objects
        if isinstance(
            result_dict.get("timestamp_from"), (datetime.date, datetime.datetime)
        ):
            result_dict["timestamp_from"] = result_dict["timestamp_from"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        if isinstance(
            result_dict.get("timestamp_to"), (datetime.date, datetime.datetime)
        ):
            result_dict["timestamp_to"] = result_dict["timestamp_to"].strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        # Commit the transaction to the database
        db.connection.commit()
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def fetch_thread_snapshots(thread_id: int, db: TiDBHandler):
    logger.info(
        f"[TIDB] Retreive thread data from the snapshot table with thread id: {thread_id}"
    )
    try:
        snapshots_list = db.execute_query_as_dict(
            SELECT_THREAD_SNAPSHOT_QUERY, params=(thread_id,)
        )

        if not snapshots_list:
            return []
        for snapshot in snapshots_list:
            if "timestamp_from" in snapshot:
                snapshot["timestamp_from"] = str(snapshot["timestamp_from"])
            if "timestamp_to" in snapshot:
                snapshot["timestamp_to"] = str(snapshot["timestamp_to"])

        return snapshots_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def remove_snapshot(snapshot_id: int, db: TiDBHandler):
    logger.info(
        f"[TIDB] Remove thread from snapshot table with snapshot id: {snapshot_id}"
    )
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(DELETE_SNAPSHOT_QUERY, (snapshot_id,))
            db.connection.commit()

            return cursor.rowcount > 0
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# def add_statistics   #jc
