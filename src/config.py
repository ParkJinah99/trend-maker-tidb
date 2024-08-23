import os
import json

LOCAL_DEV = os.getenv("LOCAL_DEV", "False").lower() == "true"

if LOCAL_DEV:
    # Load TiDB credentials from a local file
    with open("secrets/tidb_credentials.json", "r") as f:
        TIDB_CREDENTIAL = json.load(f)

    # Load SerpAPI credentials from a local file
    with open("secrets/serpapi_credentials.json", "r") as f:
        SERPAPI_CREDENTIAL_JSON = json.load(f)
        SERPAPI_CREDENTIAL = SERPAPI_CREDENTIAL_JSON["SERP_API_KEY"]

    # Load OpenAI credentials from a local file
    with open("secrets/openai_credentials.json", "r") as f:
        OPENAI_CREDENTIAL = json.load(f)

else:
    # Load TiDB credentials from environment variables
    tidb_credential_json = os.getenv("TIDB_CREDENTIAL")
    if tidb_credential_json:
        TIDB_CREDENTIAL = json.loads(tidb_credential_json)
    else:
        TIDB_CREDENTIAL = {}

    # Load SerpAPI credentials from environment variables
    SERPAPI_CREDENTIAL = os.getenv("SERP_API_KEY")

    # Load OpenAI credentials from environment variables
    OPENAI_CREDENTIAL = {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}


# logging_config.py
import logging

# Configure the logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a logger instance
logger = logging.getLogger("my_app")
