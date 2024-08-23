## Users
CREATE_USER_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    );
    """


## Thread
CREATE_THREADS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS threads (
        id INT PRIMARY KEY AUTO_INCREMENT,
        user_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        query TEXT DEFAULT NULL,
        query_embeddings JSON DEFAULT NULL,
        keywords JSON DEFAULT NULL,
        keywords_embeddings JSON DEFAULT NULL,
        category VARCHAR(255) DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
"""


CREATE_RAW_DATA_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS raw_data (
        id INT PRIMARY KEY AUTO_INCREMENT,
        thread_id INT NOT NULL,
        created_date DATETIME NOT NULL,
        queries JSON NOT NULL,
        ComparedBreakdownByRegion JSON,
        InterestByRegion JSON,
        InterestOverTime JSON,
        RelatedQueries JSON,
        YouTubeSearch JSON,
        ShoppingResults JSON,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    );
"""


CREATE_PROCESSED_DATA_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS processed_data (
        id INT PRIMARY KEY AUTO_INCREMENT,
        thread_id INT NOT NULL,
        created_date DATETIME NOT NULL,
        queries JSON NOT NULL,
        ComparedBreakdownByRegion JSON,
        InterestByRegion JSON,
        InterestOverTime JSON,
        RelatedQueries JSON,
        YouTubeSearch JSON,
        ShoppingResults JSON,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    );
    """

CREATE_THREAD_SNAPSHOTS_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS thread_snapshots (
        id INT PRIMARY KEY AUTO_INCREMENT,
        thread_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        timestamp_from DATE DEFAULT CURRENT_DATE,
        timestamp_to DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE
    );
"""

CREATE_STATISTIC_SNAPSHOT_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS statistic_snapshots (
        thread_id INT NOT NULL,
        snapshot_id INT NOT NULL,
        created_date DATETIME NOT NULL,
        ComparedBreakdownByRegion JSON,
        InterestByRegion JSON,
        InterestOverTime JSON,
        RelatedQueries JSON,
        YouTubeSearch JSON,
        ShoppingResults JSON,
        PRIMARY KEY (snapshot_id),
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
        FOREIGN KEY (snapshot_id) REFERENCES thread_snapshots(id) ON DELETE CASCADE);
    """

CREATE_STRATEGIES_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS strategy_snapshots (
        thread_id INT NOT NULL,
        snapshot_id INT NOT NULL,
        target_audience TEXT NOT NULL,
        marketing_strategies JSON NOT NULL,
        trend_summary TEXT NOT NULL,
        brand_name VARCHAR(255) NOT NULL,
        brand_description TEXT NOT NULL,
        brand_slogan TEXT NOT NULL,
        brand_color_palette JSON NOT NULL,
        logo_image LONGBLOB,
        brand_logo LONGBLOB,
        PRIMARY KEY (snapshot_id),
        FOREIGN KEY (thread_id) REFERENCES threads(id) ON DELETE CASCADE,
        FOREIGN KEY (snapshot_id) REFERENCES thread_snapshots(id) ON DELETE CASCADE
    );
"""

### Dashboard
CREATE_DASHBOARD_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS dashboard (
    id INT PRIMARY KEY AUTO_INCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_thread_number INT,
    total_user_number INT,
    total_strategy_number INT,
    total_statistic_number INT);
"""


CREATE_CAEGORY_EMBEDDINGS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS category_embeddings (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(255) NOT NULL,
    category_embedding JSON NOT NULL
);"""
