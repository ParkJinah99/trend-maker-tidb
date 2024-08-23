import requests
from requests.auth import HTTPDigestAuth
from src import config
from src.database.tidb_handler import TiDBHandler
from typing import Dict
import pandas as pd
import json
from datetime import datetime
from src.utils.data_generator.serp_api_call import get_all_data
import src.config as config
from typing import List, Dict
from src.utils.data_generator.StatProcessor import StatProcessor
from src.database.statistics import (
    insert_raw_data,
    insert_processed_data,
)
import numpy as np

from src.config import logger  # Import the logger


with open("src/utils/data_generator/country_codes.json", "r") as json_file:
    COUNTRY_CODES = json.load(json_file)


def update_raw_data(thread_id: int, keywords_list: List, country: str, db: TiDBHandler, update=False):
    """
    Process data for a given thread ID and keywords, then insert it into the database.
    Parameters:
    - thread_id: The ID associated with the thread.
    - keywords: list of kewords.
    - queries: A dictionary containing parameters for the data query.
    """
    keywords = ",".join(keywords_list)

    if update==True:
        gl = country

    else:
        # Call your function to get the data using the queries as input
        country_codes = COUNTRY_CODES.get(country.lower(), "")
        gl = country_codes.get("gl", "us")
    
    geo = gl.upper()


    # change region when country is specified
    if gl:
        region = "CITY"
    else:
        region = "COUNTRY"


    # default query parameters
    frequency = "daily"
    hl = "en"
    tz = 420
    cat = "all"
    device = "mobile"
    sort_by = "relevance"
    logger.info("Getting data from SerpAPI")

    queries, data = get_all_data(
        keywords, geo, region, tz, frequency, hl, gl, cat, device, sort_by
    )

    data_serialized = {
        key: (
            df.replace({np.nan: None}).to_dict(orient="records")
            if isinstance(df, pd.DataFrame)
            else df
        )
        for key, df in data.items()
    }
    formatted_data = {}
    # Serialize to JSON strings and handle potential issues
    try:
        formatted_data["queries"] = json.dumps(
            queries, ensure_ascii=False, allow_nan=False
        )
        for key, value in data_serialized.items():
            formatted_data[key] = json.dumps(value, ensure_ascii=False, allow_nan=False)

    except (TypeError, ValueError) as e:
        print("Error during JSON serialization:", e)
        return

    # Insert the data into the table
    insert_raw_data(thread_id, queries, formatted_data, db)

    return queries, formatted_data


def update_processed_data(thread_id, raw_queries, raw_data, db: TiDBHandler):

    stat_processor = StatProcessor(raw_queries, raw_data)
    processed_data = stat_processor.process_data()
    print("processed_data ready")

    processed_data_serialized = {
        key: (
            df.replace({np.nan: None}).to_dict(orient="records")
            if isinstance(df, pd.DataFrame)
            else df
        )
        for key, df in processed_data.items()
    }
    formatted_data = {}
    # Serialize to JSON strings and handle potential issues
    try:
        formatted_data["queries"] = json.dumps(
            raw_queries, ensure_ascii=False, allow_nan=False
        )
        for key, value in processed_data_serialized.items():
            formatted_data[key] = json.dumps(value, ensure_ascii=False, allow_nan=False)

    except (TypeError, ValueError) as e:
        print("Error during JSON serialization:", e)
        return
    insert_processed_data(thread_id, formatted_data, db)

    return processed_data
