## Users
INSERT_USER_QUERY = """
    INSERT INTO users (username, password)
    VALUES (%s, %s);
"""

SELECT_USER_BY_USERNAME_QUERY = """
    SELECT id, password
    FROM users 
    WHERE username = %s;
"""


# Threads
INSERT_THREAD_QUERY = """
    INSERT INTO threads (user_id, name, query, country, query_embeddings, keywords, keywords_embeddings)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

SELECT_USER_THREADS_QUERY = """
    SELECT id, name, query, keywords, created_at
    FROM threads
    WHERE user_id = %s;
"""

SELECT_THREAD_METADATA_QUERY = """
    SELECT id, name, query, keywords, created_at
    FROM threads
    WHERE id = %s;
"""

DELETE_THREAD_BY_ID_QUERY = """
    DELETE FROM threads 
    WHERE id = %s;
"""

UPDATE_THREAD_NAME_QUERY = """
    UPDATE threads
    SET name = %s
    WHERE id = %s;
"""


## Snapshots
INSERT_THREAD_SNAPSHOT_QUERY = """
    INSERT INTO thread_snapshots (thread_id, name, timestamp_from)
    VALUES (%s, %s, %s);
    """
SELECT_THREAD_SNAPSHOT_QUERY = """
    SELECT id, name, timestamp_from, timestamp_to
    FROM thread_snapshots
    WHERE thread_id = %s;
"""

SELECT_SNAPSHOT_QUERY = """
    SELECT id, name, timestamp_from, timestamp_to
    FROM thread_snapshots
    WHERE id = %s;
"""

DELETE_SNAPSHOT_QUERY = """
    DELETE FROM thread_snapshots
    WHERE id = %s;
"""

DELETE_SNAPSHOT_STRATEGIES_QUERY = """
    DELETE FROM strategy_snapshots
    WHERE snapshot_id = %s;
"""
DELETE_SNAPSHOT_STATISTICS_QUERY = """

"""

###### Placeholder for Statics realted SQL Queries ########

## Raw Data
INSERT_RAW_DATA_QUERY = """
    INSERT INTO raw_data (
            thread_id,
            created_date, 
            queries, 
            ComparedBreakdownByRegion, 
            InterestByRegion, 
            InterestOverTime, 
            RelatedQueries, 
            YouTubeSearch, 
            ShoppingResults
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

SELECT_RAW_DATA_QUERY = """
    SELECT *
    FROM raw_data
    WHERE thread_id = %s
    ORDER BY created_date DESC
    LIMIT 1;
"""

## Processed Data
INSERT_PROCESSED_DATA_QUERY = """
    INSERT INTO processed_data (
        thread_id,
        created_date, 
        queries, 
        ComparedBreakdownByRegion, 
        InterestByRegion, 
        InterestOverTime, 
        RelatedQueries, 
        YouTubeSearch, 
        ShoppingResults) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""
## Get the latest processed data (current)
SELECT_PROCESSED_DATA_QUERY = """
    SELECT 
        id,
        thread_id,
        created_date, 
        queries, 
        ComparedBreakdownByRegion, 
        InterestByRegion, 
        InterestOverTime, 
        RelatedQueries, 
        YouTubeSearch, 
        ShoppingResults
    FROM processed_data 
    WHERE thread_id = %s 
    ORDER BY created_date DESC
    LIMIT 1;
"""

###########################################################
## Snapshot Statistics
## Snapshots
INSERT_SNAPSHOT_DATA_QUERY = """
    INSERT INTO statistic_snapshots (
            thread_id,
            snapshot_id,
            created_date, 
            ComparedBreakdownByRegion, 
            InterestByRegion, 
            InterestOverTime, 
            RelatedQueries, 
            YouTubeSearch, 
            ShoppingResults
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
    """

## Get Snapshots
SELECT_SNAPSHOT_DATA_QUERY = """
    SELECT
        thread_id,
        snapshot_id,
        created_date,
        ComparedBreakdownByRegion,
        InterestByRegion,
        InterestOverTime,
        RelatedQueries,
        YouTubeSearch,
        ShoppingResults
    FROM statistic_snapshots
    WHERE thread_id = %s AND snapshot_id = %s
    ORDER BY created_date DESC
    LIMIT 1;
"""


## Strategies
INSERT_STRATEGY_QUERY = """
    INSERT INTO strategy_snapshots (
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
        brand_logo
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

SELECT_STRATEGIES_QUERY = """
    SELECT target_audience, marketing_strategies, trend_summary, brand_name, brand_description, brand_slogan, brand_color_palette, logo_image, brand_logo
    FROM strategy_snapshots
    WHERE snapshot_id = %s AND thread_id = %s;
"""
LOGO_VECTOR_SEARCH_QUERY = """
    SELECT meta 
    FROM logo_embeddings 
    ORDER BY Vec_Cosine_distance(embedding, %s)
    LIMIT 4;
"""

COLOR_VECTOR_SEARCH_QUERY = """
    SELECT meta
    FROM logo_colors_embeddings
    ORDER BY Vec_Cosine_distance(embedding, %s)
    LIMIT 20;
"""

SLOGAN_VECTOR_SEARCH_QUERY = """
    SELECT document
    FROM slogans_embeddings
    ORDER BY Vec_Cosine_distance(embedding, %s)
    LIMIT 20;
"""


## Dashboard
COUNT_ALL_THREADS_QUERY = """
    SELECT COUNT(id) AS total_ids
    FROM threads;
"""
COUNT_ALL_USERS_QUERY = """
    SELECT COUNT(id) AS total_ids
    FROM users;
"""

COUNT_ALL_STRATEGIES_QUERY = """
    SELECT COUNT(snapshot_id) AS total_ids
    FROM strategy_snapshots;
"""
COUNT_ALL_STATISTICS_QUERY = """
    SELECT
        SUM(CASE WHEN ComparedBreakdownByRegion != 'null' THEN 1 ELSE 0 END) +
        SUM(CASE WHEN InterestByRegion != 'null' THEN 1 ELSE 0 END) +
        SUM(CASE WHEN InterestOverTime != 'null' THEN 1 ELSE 0 END) +
        SUM(CASE WHEN RelatedQueries != 'null' THEN 1 ELSE 0 END) +
        SUM(CASE WHEN YouTubeSearch != 'null' THEN 1 ELSE 0 END) +
        SUM(CASE WHEN ShoppingResults != 'null' THEN 1 ELSE 0 END) AS AggregatedCount_NotNullValues
    FROM
        processed_data;
"""

INSERT_ALL_DASHBOARD_QUERY = """
    INSERT INTO dashboard 
    (total_thread_number, 
    total_user_number, 
    total_strategy_number, 
    total_statistic_number)
    VALUES (%s, %s, %s, %s);
"""

GET_PREVIOUS_DASHBOARD_QUERY = """
    SELECT 
        total_thread_number,
        total_user_number,
        total_strategy_number,
        total_statistic_number
    FROM 
        dashboard
    WHERE 
        DATE(created_at) = CURDATE() - INTERVAL 1 DAY
    ORDER BY 
        created_at ASC
    LIMIT 1;
"""

SELECT_COUNTRY_QUERY = """
SELECT country, COUNT(*) as count
FROM threads
GROUP BY country;
"""


SELECT_QUERIES_TIMELINE_QUERY = """
    SELECT DATE(created_at) AS creation_date, COUNT(id) AS daily_thread_count
    FROM threads
    GROUP BY DATE(created_at)
    ORDER BY creation_date;
"""

SELECT_ALL_QUERY = """
    SELECT id, query, query_embeddings 
    FROM threads;
"""
GET_CATEGORY_EMBEDDINGS_QUERY = """
    SELECT document, embedding
    FROM category_embeddings;
"""
MATCH_QUERY_TO_CATEGORY_QUERY = """
    SELECT document
    FROM category_embeddings
    ORDER BY VEC_COSINE_DISTANCE(embedding, %s) ASC
    LIMIT 1;
    """

UPDATE_QUERY_CATEGORIES_QUERY = """
    UPDATE threads 
    SET category = %s 
    WHERE id = %s;
"""

GET_TOP_CATEGORIES_QUERY = """
    SELECT category, COUNT(*) as total_queries
    FROM threads
    GROUP BY category
    ORDER BY total_queries DESC
    LIMIT 10;
"""
