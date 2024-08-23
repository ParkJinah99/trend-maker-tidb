import asyncio
from src.database.init_tidb import init_tidb
from src.database.init_db.sql_queries import (
    CREATE_USER_TABLE_SQL,
    CREATE_THREADS_TABLE_SQL,
    CREATE_RAW_DATA_TABLE_SQL,
    CREATE_PROCESSED_DATA_TABLE_SQL,
    CREATE_THREAD_SNAPSHOTS_TABLE_SQL,
    CREATE_STATISTIC_SNAPSHOT_TABLE_SQL,
    CREATE_STRATEGIES_TABLE_SQL,
    CREATE_DASHBOARD_TABLE_SQL,
    CREATE_CAEGORY_EMBEDDINGS_TABLE_SQL,
)


async def initialize_database():
    db = init_tidb()
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(CREATE_STRATEGIES_TABLE_SQL)
            db.connection.commit()

        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
    finally:
        db.connection.close()


if __name__ == "__main__":
    asyncio.run(initialize_database())
    # asyncio.run(initialize_database())
