from fastapi import HTTPException
from typing import List, Dict
import json
import pandas as pd

from src.database.tidb_handler import TiDBHandler
from src.database.sql_queries import (
    INSERT_STRATEGY_QUERY,
    SELECT_STRATEGIES_QUERY,
    LOGO_VECTOR_SEARCH_QUERY,
    COLOR_VECTOR_SEARCH_QUERY,
    SLOGAN_VECTOR_SEARCH_QUERY,
)
from src.utils.openai.embeddings.generate_embeddings import get_embeddings
from src.config import logger


def add_strategies(thread_id: int, snapshot_id: int, strategies: Dict, db: TiDBHandler):
    logger.info(
        f"[TIDB] Insert strategies into TIDB table with thread id and snapshot id: {thread_id}, {snapshot_id}"
    )
    try:
        # Extract the fields from the strategies dictionary
        target_audience = strategies["target_audience"]
        marketing_strategies = json.dumps(strategies["marketing_strategies"])
        trend_summary = strategies["trend_summary"]
        brand_name = strategies["brand_name"]
        brand_description = strategies["brand_description"]
        brand_slogan = strategies["brand_slogan"]
        brand_color_palette = json.dumps(strategies["brand_color_palette"])
        logo_image = json.dumps(strategies["logo_image"])  # This is binary data
        brand_logo = json.dumps(strategies["brand_logo"])

        # Execute the query with parameterized inputs
        with db.connection.cursor() as cursor:
            cursor.execute(
                INSERT_STRATEGY_QUERY,
                (
                    thread_id,
                    snapshot_id,
                    target_audience,
                    marketing_strategies,
                    trend_summary,
                    brand_name,
                    brand_description,
                    brand_slogan,
                    brand_color_palette,
                    logo_image,
                    brand_logo,
                ),
            )
            db.connection.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def fetch_snapshot_strategies(thread_id: int, snapshot_id: int, db: TiDBHandler):
    logger.info(
        f"[TIDB] Retreive strategies from the snapshot table with thread id and snapshot id: {thread_id}, {snapshot_id}"
    )
    try:
        # Execute the query using execute_query_as_dict with parameters
        result_list = db.execute_query_as_dict(
            SELECT_STRATEGIES_QUERY, params=(snapshot_id, thread_id)
        )

        # Check if any result was returned
        if not result_list:
            return None

        # Return the first result as a dictionary
        return result_list[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def vector_search_brand(brand_metadata: Dict, db: TiDBHandler) -> Dict:
    logger.info(f"[TIDB] vector seach the brand data")
    brand_description = brand_metadata["brand_description"]
    description_embeddings = get_embeddings(brand_description)

    queries = {
        "logos": LOGO_VECTOR_SEARCH_QUERY,
        "colors": COLOR_VECTOR_SEARCH_QUERY,
        "slogans": SLOGAN_VECTOR_SEARCH_QUERY,
    }

    try:
        results = {}
        description_embeddings = json.dumps(description_embeddings)
        for key, query_template in queries.items():
            # Execute the query with parameterized embeddings
            result_list = db.execute_query_as_dict(
                query_template, params=(description_embeddings,)
            )

            if not result_list:
                results[key] = []
                continue

            if key == "logos":
                # Parse the JSON strings into dictionaries before accessing the "image" key
                results[key] = [
                    json.loads(item["meta"])["image"] for item in result_list
                ]

            elif key == "colors":
                # Parse the JSON strings in "meta" column into dictionaries
                color_metadata_list = [json.loads(item["meta"]) for item in result_list]

                # Normalize the list of dictionaries into a DataFrame
                color_metadata_df = pd.json_normalize(color_metadata_list)

                # Identify the maximum values
                max_sentiment = color_metadata_df.loc[
                    color_metadata_df["sentiment"].idxmax()
                ]
                max_reach = color_metadata_df.loc[color_metadata_df["reach"].idxmax()]
                max_domain = color_metadata_df.loc[
                    color_metadata_df["domain_influence"].idxmax()
                ]

                # Construct the final output
                results[key] = [
                    {
                        "category": "sentiment",
                        "rgb": max_sentiment["rgb"],
                        "brand_name": max_sentiment["name"],
                    },
                    {
                        "category": "reach",
                        "rgb": max_reach["rgb"],
                        "brand_name": max_reach["name"],
                    },
                    {
                        "category": "domain",
                        "rgb": max_domain["rgb"],
                        "brand_name": max_domain["name"],
                    },
                ]

            elif key == "slogans":
                # Directly retrieve the slogans
                results[key] = [item["document"] for item in result_list]

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
