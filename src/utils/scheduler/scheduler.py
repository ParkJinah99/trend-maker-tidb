import schedule
import time
from datetime import datetime
from pytz import timezone
import logging
import json
from src.database.init_tidb import init_tidb
from fastapi import HTTPException
from src.utils.data_generator.data_handler import update_raw_data
from src.config import logger

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_threads_and_queries(db):
    logger.info(f"[OpenAI] Retrieve threads and queries")
    query = "SELECT DISTINCT Thread_ID, queries FROM Raw_data"
    threads_queries = []
    try:
        with db.connection.cursor() as cursor:
            cursor.execute(query)
            result = cursor.fetchall()

        for row in result:
            thread_id = row[0]
            queries_json = row[1]
            queries = json.loads(queries_json)  # Parse the JSON string
            keywords = queries.pop("q")  # Extract keywords from the "q" key

            threads_queries.append(
                {"thread_id": thread_id, "keywords": keywords, "queries": queries}
            )
    except Exception as e:
        logging.error(f"Failed to fetch threads and queries: {e}")

    return threads_queries


def run_scheduler(db):
    logger.info(f"[OpenAI] Run scheduler")
    threads_queries = fetch_threads_and_queries(db)

    for item in threads_queries:
        thread_id = item["thread_id"]
        keywords = item["keywords"].split(",")
        raw_queries = item["queries"]
        country = raw_queries.get("gl", "")

        try:
            # Fetch and process trend data with update - True
            update_raw_data(thread_id, keywords, country, db, True)
            print("Update completed for thread_id:", thread_id)

        except Exception as e:
            logging.error(f"Error in updating threadID: {thread_id}. Error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"An error occurred while initiating the query: {str(e)}",
            )


def job():
    """Job to be scheduled."""
    logging.info("Starting the scheduled update...")
    # Initialize the TiDBHandler instance for dependency injection\
    print("Scheduled job is running")  # For quick visibility
    db = init_tidb()
    run_scheduler(db)


def schedule_daily_job():
    # Schedule the job every day at 12am SGT
    logger.info(f"[OpenAI] Schedule the job daily at 12am SGT")
    sgt = timezone("Asia/Singapore")

    def run_at_sgt_midnight():
        current_time = datetime.now(sgt).time()
        if current_time.hour == 00 and current_time.minute == 00:
            job()

    # schedule.every().day.at("00:00").do(run_at_sgt_midnight)
    schedule.every().day.at("00:00").do(run_at_sgt_midnight)

    logging.info("Scheduler set to run daily at 12am SGT.")

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    schedule_daily_job()
