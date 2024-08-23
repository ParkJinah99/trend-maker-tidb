from src.database.sql_queries import (
    COUNT_ALL_THREADS_QUERY,
    COUNT_ALL_USERS_QUERY,
    COUNT_ALL_STRATEGIES_QUERY,
    COUNT_ALL_STATISTICS_QUERY,
    SELECT_COUNTRY_QUERY,
    INSERT_ALL_DASHBOARD_QUERY,
    GET_PREVIOUS_DASHBOARD_QUERY,
    SELECT_QUERIES_TIMELINE_QUERY,
    SELECT_ALL_QUERY,
    MATCH_QUERY_TO_CATEGORY_QUERY,
    GET_CATEGORY_EMBEDDINGS_QUERY,
    UPDATE_QUERY_CATEGORIES_QUERY,
    GET_TOP_CATEGORIES_QUERY,
)
from src.database import TiDBHandler
import numpy as np
import json
from typing import Dict
import pandas as pd
from src.config import logger


# Aggregated counts
def get_aggregated_counts(db: TiDBHandler):
    with db.connection.cursor() as cursor:
        cursor.execute(COUNT_ALL_THREADS_QUERY)
        queries_number = cursor.fetchone()[0]

        cursor.execute(COUNT_ALL_USERS_QUERY)
        users_number = cursor.fetchone()[0]

        cursor.execute(COUNT_ALL_STRATEGIES_QUERY)
        strategies_number = cursor.fetchone()[0]

        cursor.execute(COUNT_ALL_STATISTICS_QUERY)
        statistics_number = cursor.fetchone()[0]
    return {
        "queries_number": int(queries_number),
        "users_number": int(users_number),
        "strategies_number": int(strategies_number),
        "statistics_number": int(statistics_number),
    }


def update_aggregated_counts(aggregated_counts: Dict, db: TiDBHandler):
    with db.connection.cursor() as cursor:
        cursor.execute(
            INSERT_ALL_DASHBOARD_QUERY,
            (
                aggregated_counts["queries_number"],
                aggregated_counts["users_number"],
                aggregated_counts["strategies_number"],
                aggregated_counts["statistics_number"],
            ),
        )
    db.connection.commit()


def retrieve_previous_aggregated_counts(db: TiDBHandler):
    try:
        result_df = db.execute_query_as_dict(GET_PREVIOUS_DASHBOARD_QUERY)[0]
    except:
        result_df = None
    if result_df is None:
        return {
            "queries_number": 0,
            "users_number": 0,
            "strategies_number": 0,
            "statistics_number": 0,
        }
    result_dict = {
        "queries_number": int(result_df["total_thread_number"]),
        "users_number": int(result_df["total_user_number"]),
        "strategies_number": int(result_df["total_strategy_number"]),
        "statistics_number": int(result_df["total_statistic_number"]),
    }
    return result_dict


# Queries over time
def get_queries_over_time(db: TiDBHandler):
    result_df = db.execute_query_as_dict(SELECT_QUERIES_TIMELINE_QUERY)
    result_df = pd.DataFrame(result_df)
    result_df["creation_date"] = result_df["creation_date"].astype(
        str
    )  # Convert dates to strings
    result_dict = result_df.to_dict(orient="records")
    db.connection.commit()  # Ensure any transaction is committed

    return result_dict


def get_query_countries(db: TiDBHandler):
    result = db.execute_query_as_dict(SELECT_COUNTRY_QUERY)
    result_dict = {}
    for row in result:
        result_dict[row["country"]] = row["count"]
    return result_dict


# Fetch category embeddings
def fetch_category_embeddings(db: TiDBHandler):
    with db.connection.cursor() as cursor:
        cursor.execute(GET_CATEGORY_EMBEDDINGS_QUERY)
        result = cursor.fetchall()

    category_names = [row[0] for row in result]
    category_embeddings = np.array(
        [json.loads(row[1]) for row in result]
    )  # Convert JSON to list of floats

    return category_names, category_embeddings


# Fetch all embeddings
def fetch_all_embeddings(db: TiDBHandler):
    with db.connection.cursor() as cursor:
        cursor.execute(SELECT_ALL_QUERY)
        result = cursor.fetchall()

    thread_ids = [row[0] for row in result if row[1] != ""]
    queries = [row[1] for row in result if row[1] != ""]
    embeddings = np.array(
        [json.loads(row[2]) for row in result if row[1] != ""]
    )  # Convert string to list of floats

    return thread_ids, queries, embeddings


# Match query to category using vector search
def match_query_to_category(db: TiDBHandler, query_embedding: np.array):
    query_embedding_str = json.dumps(query_embedding.tolist())

    with db.connection.cursor() as cursor:
        cursor.execute(MATCH_QUERY_TO_CATEGORY_QUERY, (query_embedding_str,))
        result = cursor.fetchone()

    return result[0] if result else None


# Update query categories in the database
def update_query_categories(thread_ids, categories, db: TiDBHandler):
    with db.connection.cursor() as cursor:
        for thread_id, category in zip(thread_ids, categories):
            cursor.execute(UPDATE_QUERY_CATEGORIES_QUERY, (category, thread_id))
    db.connection.commit()


# Get top categories
def get_top_categories(db: TiDBHandler):
    with db.connection.cursor() as cursor:
        cursor.execute(GET_TOP_CATEGORIES_QUERY)
        result = cursor.fetchall()

    return [{"category": row[0], "total_queries": row[1]} for row in result]
