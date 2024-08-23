import json
from datetime import datetime
import numpy as np
from typing import List, Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.database import TiDBHandler
from src.database.init_tidb import init_tidb
from src.database.threads import (
    create_thread,
    fetch_user_threads,
    update_thread_name,
    create_thread_snapshot,
    fetch_thread_metadata,
    fetch_thread_snapshots,
    remove_thread_by_id,
    remove_snapshot,
)
from src.database.strategies import (
    add_strategies,
    fetch_snapshot_strategies,
)

from src.api.threads.schemas import QueryRequest

from src.utils.openai.embeddings.generate_embeddings import get_embeddings
from src.utils.openai.query_processor.process_query import process_query
from src.utils.data_generator.data_handler import update_raw_data, update_processed_data
from src.utils.openai.strategy_creator.create_strategy import (
    create_general_strategy,
    create_brand_identities,
)

from src.database.statistics import (
    get_raw_data,
    get_processed_data,
    insert_snapshot_data,
    get_snapshot_data,
)

from src.config import logger  # Import the logger


threads_router = APIRouter()


@threads_router.post("/")
async def initiate_query(
    request: QueryRequest,
    db: TiDBHandler = Depends(init_tidb),
):
    try:
        logger.info(f"[Threads] Initiate query endpoint called with request: {request}")
        user_id = request.user_id
        user_query = request.user_query
        country = request.country

        # Process the user's query to extract metadata and keywords
        query_metadata = process_query(user_query)
        keywords = query_metadata.get("keywords", [])
        thread_name = query_metadata.get("name", "Untitled Thread")

        # Generate embeddings for the query and its keywords
        query_embeddings = get_embeddings(user_query)
        keywords_embeddings = get_embeddings(", ".join(keywords))

        # Create a new thread in the database
        thread_id = create_thread(
            user_id=user_id,
            name=thread_name,
            query=user_query,
            country=country,
            query_embeddings=query_embeddings,
            keywords=keywords,
            keywords_embeddings=keywords_embeddings,
            db=db,
        )

        # Fetch and process trend data
        raw_queries, raw_data = update_raw_data(thread_id, keywords, country, db)
        processed_data = update_processed_data(thread_id, raw_queries, raw_data, db)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thread initialized successfully",
                "data": {"thread_id": thread_id, "processed_data": processed_data},
            },
        )

    except Exception as e:
        # Log the exception if you have a logger setup, e.g., logger.error(f"Error initiating query: {e}")
        remove_thread_by_id(thread_id, db)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while initiating the query: {str(e)}",
        )


@threads_router.get("/user/{user_id}")
async def read_user_threads(user_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Threads] Retrieve user threads with user_id: {user_id}")

    try:
        user_threads = fetch_user_threads(user_id, db)

        if not user_threads:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "No threads found for the given user.",
                    "data": None,
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Threads retrieved successfully.",
                "data": user_threads,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve user threads.",
                "error": str(e),
            },
        )


@threads_router.put("/rename/{thread_id}/{new_name}")
async def rename_thread_name(
    thread_id: int, new_name: str, db: TiDBHandler = Depends(init_tidb)
):
    logger.info(f"[Threads] Renaming thread endpoint by thread id: {thread_id}")
    try:
        updated_thread = update_thread_name(thread_id, new_name, db)

        if not updated_thread:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Thread not found.",
                    "data": None,
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thread name updated successfully.",
                "data": updated_thread,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to update thread name.",
                "error": str(e),
            },
        )


@threads_router.get("/metadata/{thread_id}")
async def read_thread_metadata(thread_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Threads] Retreive thread metadata with thread id: {thread_id}")
    try:
        thread_metadata = fetch_thread_metadata(thread_id, db)

        if not thread_metadata:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Thread metadata not found.",
                    "data": None,
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Thread metadata retrieved successfully.",
                "data": thread_metadata,
            },
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve thread metadata.",
                "error": str(e),
            },
        )


@threads_router.delete("/{thread_id}")
async def delete_thread(thread_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Threads] Renaming thread endpoint by thread id: {thread_id}")
    try:
        remove_thread_by_id(thread_id, db)
        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "Thread deleted successfully."},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to delete thread.",
                "error": str(e),
            },
        )


###############TO DO###############
@threads_router.get("/statistics/{thread_id}")
async def get_current_statistics(thread_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(
        f"Retrive or update processed data from tidb with thread id: {thread_id}"
    )
    try:
        processed_data = get_processed_data(thread_id, db)
        if processed_data is None:
            raw_data, raw_queries = get_raw_data(thread_id, db)
            processed_data = update_processed_data(thread_id, raw_queries, raw_data, db)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Statistics retrieved successfully.",
                "data": processed_data,
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Failed to retrieve statistics.",
                "error": str(e),
            },
        )


@threads_router.get("/snapshot/{thread_id}")
async def read_threads_snapshot(thread_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(
        f"[Threads] Retrieving snapshot list of data with thread id: {thread_id}"
    )
    try:
        snapshot_list = fetch_thread_snapshots(thread_id, db)

        if not snapshot_list:
            return JSONResponse(
                status_code=201,
                content={
                    "status": "success",
                    "message": "No snapshots found for the given thread.",
                    "data": [],
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Snapshots retrieved successfully.",
                "data": snapshot_list,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve snapshots.",
                "error": str(e),
            },
        )


###############TO DO###############
@threads_router.post("/snapshot/{thread_id}")
async def take_threads_snapshot(thread_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(
        f"Retrieving processed data to snapshot table and generate stretegies with thread id: {thread_id}"
    )
    try:
        thread_metadata = fetch_thread_metadata(thread_id, db)
        snapshot_metadata = create_thread_snapshot(thread_metadata, db)

        query = thread_metadata["query"]
        keywords = thread_metadata["keywords"]

        # Retrieving processed data and saving to snapshot statistics table
        processed_data = get_processed_data(thread_id, db)
        insert_snapshot_data(thread_id, snapshot_metadata["id"], processed_data, db)

        # Generating strategies
        strategies_metadata = create_general_strategy(query, keywords, processed_data)
        brand_identities = create_brand_identities(strategies_metadata, db)

        # Merging strategy metadata with brand identities
        strategies_metadata.update(brand_identities)
        add_strategies(thread_id, snapshot_metadata["id"], strategies_metadata, db)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Snapshot created successfully.",
                "data": {
                    "snapshot": snapshot_metadata,
                    "statistics": processed_data,  # Uncomment if needed
                    "strategies": strategies_metadata,  # Uncomment if needed
                },
            },
        )
    except Exception as e:
        remove_snapshot(snapshot_metadata["id"], db)
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to create snapshot.",
                "error": str(e),
            },
        )


@threads_router.get("/snapshot/strategies/{thread_id}/{snapshot_id}")
async def get_strategies_for_snapshot(
    thread_id: int, snapshot_id: int, db: TiDBHandler = Depends(init_tidb)
):
    logger.info(
        f"Retrieving strategies with thread id and snapshot id: {thread_id}, {snapshot_id}"
    )
    try:
        strategies_metadata = fetch_snapshot_strategies(thread_id, snapshot_id, db)

        if strategies_metadata:
            strategies_metadata["logo_image"] = json.loads(
                strategies_metadata.get("logo_image", "")
            )
            strategies_metadata["brand_logo"] = json.loads(
                strategies_metadata.get("brand_logo", "")
            )
            strategies_metadata["brand_name"] = strategies_metadata.get(
                "brand_name", ""
            ).upper()

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Strategies retrieved successfully.",
                "data": strategies_metadata,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve strategies for the snapshot.",
                "error": str(e),
            },
        )


###############TO DO###############
@threads_router.get("/snapshot/statistics/{thread_id}/{snapshot_id}")
async def get_statistics_for_snapshot(
    thread_id: int, snapshot_id: int, db: TiDBHandler = Depends(init_tidb)
):
    logger.info(
        f"Retrieve processed data from the snapshot table with thread id and snapshot id: {thread_id}, {snapshot_id}"
    )
    try:
        # processed_data = get_snapshot_statistics(thread_id, snapshot_id, db)
        processed_data = get_snapshot_data(thread_id, snapshot_id, db)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Statistics retrieved successfully.",
                "data": processed_data,
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to retrieve statistics for the snapshot.",
                "error": str(e),
            },
        )


@threads_router.delete("/snapshot/{snapshot_id}", response_model=Dict)
async def delete_snapshot_by_id(snapshot_id: int, db: TiDBHandler = Depends(init_tidb)):
    logger.info(
        f"[Threads] Deleting data from the snapshot tabe with snapshot id: {snapshot_id}"
    )
    try:
        deleted = remove_snapshot(snapshot_id, db)

        if not deleted:
            return JSONResponse(
                status_code=404,
                content={
                    "status": "error",
                    "message": "Snapshot not found.",
                    "data": None,
                },
            )

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Snapshot deleted successfully.",
                "data": {"snapshot_id": snapshot_id},
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "error",
                "message": "Failed to delete snapshot.",
                "error": str(e),
            },
        )
