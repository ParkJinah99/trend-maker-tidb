from fastapi import HTTPException
from typing import List, Dict
from src.database.tidb_handler import TiDBHandler
import json
from datetime import datetime
import pandas as pd
from src.database.sql_queries import (
    INSERT_RAW_DATA_QUERY,
    INSERT_PROCESSED_DATA_QUERY,
    INSERT_SNAPSHOT_DATA_QUERY,
    SELECT_RAW_DATA_QUERY,
    SELECT_PROCESSED_DATA_QUERY,
    SELECT_SNAPSHOT_DATA_QUERY,
)
import numpy as np
from src.config import logger


def insert_raw_data(thread_id: int, queries: Dict, data: Dict, db: TiDBHandler):
    """
    Inserts raw data into the specified table, with each data type in a separate column.

    Parameters:
    - thread_id: The ID associated with the thread (input variable).
    - queries: A dictionary of the queries used to generate the data.
    - data: A dictionary containing the retrieved data for each data type.
    """
    with db.connection.cursor() as cursor:
        created_date = datetime.now()
        queries = json.dumps(queries)
        compared_breakdown_by_region = json.dumps(
            data.get("ComparedBreakdownByRegion", None)
        )
        interest_by_region = json.dumps(data.get("InterestByRegion", None))
        interest_over_time = json.dumps(data.get("InterestOverTime", None))
        related_queries = json.dumps(data.get("RelatedQueries", None))
        youtube_search = json.dumps(data.get("YouTubeSearch", None))
        shopping_results = json.dumps(data.get("ShoppingResults", None))

        cursor.execute(
            INSERT_RAW_DATA_QUERY,
            (
                thread_id,
                created_date,
                queries,
                compared_breakdown_by_region,
                interest_by_region,
                interest_over_time,
                related_queries,
                youtube_search,
                shopping_results,
            ),
        )
        db.connection.commit()


def insert_processed_data(thread_id: int, data: dict, db: TiDBHandler):
    logger.info(
        f"[TIDB] Insert processed data into TIDB table with thread id: {thread_id}"
    )
    with db.connection.cursor() as cursor:
        created_date = datetime.now().isoformat()

        cursor.execute(
            INSERT_PROCESSED_DATA_QUERY,
            (
                thread_id,
                created_date,
                data.get("queries"),
                data.get("ComparedBreakdownByRegion"),
                data.get("InterestByRegion"),
                data.get("InterestOverTime"),
                data.get("RelatedQueries"),
                data.get("YouTubeSearch"),
                data.get("ShoppingResults"),
            ),
        )
        db.connection.commit()


def insert_snapshot_data(thread_id: int, snapshot_id: int, data: Dict, db: TiDBHandler):
    logger.info(
        f"[TIDB] Insert snapshot data into TIDB table with thread id and snapshot id: {thread_id}, {snapshot_id}"
    )
    """
    Inserts snapshot data into the specified table, with each data type in a separate column.

    Parameters:
    - thread_id: The ID associated with the thread (input variable).
    - snapshot_id: The ID associated with the snapshot (input variable).
    - data: A dictionary containing the retrieved data for each data type.
    - db: An instance of TiDBHandler for database operations.
    """
    with db.connection.cursor() as cursor:
        created_date = datetime.now().isoformat()
        compared_breakdown_by_region = json.dumps(
            data.get("ComparedBreakdownByRegion", None)
        )
        interest_by_region = json.dumps(data.get("InterestByRegion", None))
        interest_over_time = json.dumps(data.get("InterestOverTime", None))
        related_queries = json.dumps(data.get("RelatedQueries", None))
        youtube_search = json.dumps(data.get("YouTubeSearch", None))
        shopping_results = json.dumps(data.get("ShoppingResults", None))
        # Prepare the query parameters, ensuring all data is JSON-serialized
        query_params = (
            thread_id,
            snapshot_id,
            created_date,
            compared_breakdown_by_region,
            interest_by_region,
            interest_over_time,
            related_queries,
            youtube_search,
            shopping_results,
        )

        cursor.execute(INSERT_SNAPSHOT_DATA_QUERY, query_params)
        db.connection.commit()


def get_raw_data(thread_id: int, db: TiDBHandler):
    logger.info(
        f"[TIDB] Retrieve raw data from TIDB table with thread id : {thread_id}"
    )
    result_df = db.execute_query_as_dict(SELECT_RAW_DATA_QUERY, (thread_id,))
    raw_data_metadata = result_df[0]
    queries = raw_data_metadata.get("queries", None)
    raw_data = {
        "ComparedBreakdownByRegion": raw_data_metadata.get(
            "ComparedBreakdownByRegion", None
        ),
        "InterestByRegion": raw_data_metadata.get("InterestByRegion", None),
        "InterestOverTime": raw_data_metadata.get("InterestOverTime", None),
        "RelatedQueries": raw_data_metadata.get("RelatedQueries", None),
        "YouTubeSearch": raw_data_metadata.get("YouTubeSearch", None),
        "ShoppingResults": raw_data_metadata.get("ShoppingResults", None),
    }
    return raw_data, queries


def get_processed_data(thread_id: int, db: TiDBHandler):
    logger.info(
        f"[TIDB] Retrieve processed data from TIDB table with thread id: {thread_id}"
    )
    """
    Retrieves and processes the most recent data for the given thread_id.

    Parameters:
    - thread_id: The ID associated with the thread (input variable).
    - db: An instance of TiDBHandler for database operations.

    Returns:
    - A dictionary containing the processed data.
    """
    result_df = db.execute_query_as_dict(SELECT_PROCESSED_DATA_QUERY, (thread_id,))
    processed_data = result_df[0]

    if not processed_data:
        return None

    created_date = processed_data.get("created_date", None)
    if created_date:
        created_date = created_date.strftime("%Y-%m-%d %H:%M:%S")
    data = {
        "id": processed_data["id"],
        "thread_id": processed_data["thread_id"],
        "created_date": created_date,
        "queries": safe_json_load(processed_data["queries"]),
        "ComparedBreakdownByRegion": safe_json_load(
            processed_data["ComparedBreakdownByRegion"]
        ),
        "InterestByRegion": safe_json_load(processed_data["InterestByRegion"]),
        "InterestOverTime": safe_json_load(processed_data["InterestOverTime"]),
        "RelatedQueries": safe_json_load(processed_data["RelatedQueries"]),
        "YouTubeSearch": safe_json_load(processed_data["YouTubeSearch"]),
        "ShoppingResults": safe_json_load(processed_data["ShoppingResults"]),
    }

    return data


def get_snapshot_data(thread_id: int, snapshot_id: int, db: TiDBHandler):
    logger.info(
        f"[TIDB] Retrieve snapshot data from TIDB table with thread id and snapshot id: {thread_id}, {snapshot_id}"
    )
    """
    Retrieves a snapshot of data for the given thread_id and snapshot_id.

    Parameters:
    - thread_id: The ID associated with the thread (input variable).
    - snapshot_id: The ID associated with the snapshot (input variable).
    - db: An instance of TiDBHandler for database operations.

    Returns:
    - A dictionary containing the snapshot data.
    """
    snapshot_metadata = db.execute_query_as_dict(
        SELECT_SNAPSHOT_DATA_QUERY, (thread_id, snapshot_id)
    )[0]

    if not snapshot_metadata:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for Thread_ID: {thread_id} and Snapshot_ID: {snapshot_id}",
        )

    data = {
        "thread_id": snapshot_metadata["thread_id"],
        "snapshot_id": snapshot_metadata["snapshot_id"],
        "created_date": (
            snapshot_metadata["created_date"].strftime("%Y-%m-%d %H:%M:%S")
        ),
        "ComparedBreakdownByRegion": safe_json_load(
            snapshot_metadata["ComparedBreakdownByRegion"]
        ),
        "InterestByRegion": safe_json_load(snapshot_metadata["InterestByRegion"]),
        "InterestOverTime": safe_json_load(snapshot_metadata["InterestOverTime"]),
        "RelatedQueries": safe_json_load(snapshot_metadata["RelatedQueries"]),
        "YouTubeSearch": safe_json_load(snapshot_metadata["YouTubeSearch"]),
        "ShoppingResults": safe_json_load(snapshot_metadata["ShoppingResults"]),
    }

    return data


def safe_json_load(value):
    """
    Safely loads JSON data from a string, returning an empty dictionary on failure.

    Parameters:
    - value: The JSON string to load.

    Returns:
    - A dictionary parsed from the JSON string, or an empty dictionary if parsing fails.
    """
    try:
        return json.loads(value) if value else {}
    except json.JSONDecodeError:
        return {}
