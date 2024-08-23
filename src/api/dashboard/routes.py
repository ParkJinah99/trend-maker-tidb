import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from src.config import logger
from src.database import TiDBHandler
from src.database.init_tidb import init_tidb
from src.database.dashboard import (
    get_aggregated_counts,
    update_aggregated_counts,
    retrieve_previous_aggregated_counts,
    get_query_countries,
    get_queries_over_time,
    fetch_all_embeddings,
    fetch_category_embeddings,
    update_query_categories,
    get_top_categories,
    match_query_to_category,
)

dashboard_router = APIRouter()


@dashboard_router.get("/aggregated_counts")
async def retrieve_aggregated_counts(db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Dashboard] Retrieve and update aggregated counts")
    try:
        aggregated_counts = get_aggregated_counts(db)
        update_aggregated_counts(aggregated_counts, db)
        pre_counts = retrieve_previous_aggregated_counts(db)
        for key, value in pre_counts.items():
            aggregated_counts[f"diff_{key}"] = aggregated_counts[key] - value

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": aggregated_counts,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@dashboard_router.get("/aggregated_country_counts")
async def retrieve_country_counts(db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Dashboard] Retrieve country counts")
    try:
        country_counts = get_query_countries(db)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": country_counts,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@dashboard_router.get("/queries-over-time")
async def retrieve_query_activity_timeline(db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Dashboard] Retrieve activity timeline of the queries")
    try:
        queries_over_time = get_queries_over_time(db)
        # in df format with columns: creation_date, daily_thread_count
        """
        [{"creation_date": "2024-08-05", "daily_thread_count": 1}, 
        {"creation_date": "2024-08-06", "daily_thread_count": 2}, 
        {"creation_date": "2024-08-07", "daily_thread_count": 1}, 
        {"creation_date": "2024-08-11", "daily_thread_count": 2}, 
        {"creation_date": "2024-08-14", "daily_thread_count": 1}, 
        {"creation_date": "2024-08-18", "daily_thread_count": 19}]
        """
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": queries_over_time,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# TODO
@dashboard_router.get("/keyword_ranking")
async def retrieve_keyword_ranking(db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Dashboard] Retrieve keywords ranking")
    # Functionality not implemented yet
    return JSONResponse(
        status_code=501,
        content={
            "status": "error",
            "detail": "Keyword ranking functionality is not yet implemented.",
        },
    )


@dashboard_router.get("/top_categories")
async def retrieve_top_categories(db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Dashboard] Retrieve top categories of the queries")
    try:
        thread_ids, queries, embeddings = fetch_all_embeddings(db)

        # Ensure embeddings is a 2D numpy array
        embeddings = np.array(embeddings)
        if embeddings.ndim != 2:
            raise ValueError(
                "Embeddings array is not 2D. Please check the data format.",
                response_model=JSONResponse,
            )

        # Categorize each query using vector search
        named_categories = [
            match_query_to_category(db, embedding) for embedding in embeddings
        ]

        # Update categories in the database
        update_query_categories(thread_ids, named_categories, db)

        # Fetch and return the top categories
        top_categories = get_top_categories(db)
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": {"top_categories": top_categories},
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@dashboard_router.get("/queries-embeddings")
async def retreive_queries_embeddings(db: TiDBHandler = Depends(init_tidb)):
    logger.info(f"[Dashboard] Retrieve queries-embeddings")
    try:
        _, queries, embeddings = fetch_all_embeddings(db)
        category_names, category_embeddings = fetch_category_embeddings(db)
        # Convert embeddings from numpy array to list of lists for JSON serialization
        embeddings = [
            embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            for embedding in embeddings
        ]
        category_embeddings = [
            embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            for embedding in category_embeddings
        ]

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": {
                    "queries": queries,
                    "embeddings": embeddings,
                    "category_names": category_names,
                    "category_embeddings": category_embeddings,
                },
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
