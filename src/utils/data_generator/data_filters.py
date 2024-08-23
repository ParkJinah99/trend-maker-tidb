import pandas as pd
from src.config import logger  # Import the logger


def filter_ComparedBreakdownByRegion(data):
    """
    Filters and transforms the compared breakdown by region data into a wide format DataFrame.

    Parameters:
    - data: The JSON response from the Google Trends API.

    Returns:
    - A pandas DataFrame where each row is a location and each column is a query with the extracted value.
    """
    if not data or data == "[]":
        logger.warning(
            "Received empty or invalid data for Compared Breakdown By Region"
        )
        return []

    logger.info("Results from Google Trends API: Compared Breakdown By Region")
    regions = data.get("compared_breakdown_by_region", [])
    cleaned_data = []
    for region in regions:
        location = region.get("location", "")
        for value in region.get("values", []):
            cleaned_data.append(
                {
                    "Location": location,
                    "Query": value.get("query", ""),
                    "Extracted Value": value.get("extracted_value", 0),
                }
            )

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    df_wide = df.pivot(
        index="Location", columns="Query", values="Extracted Value"
    ).reset_index()

    return df_wide


def filter_InterestByRegion(data):
    """
    Filters the interest by region data to create a structured DataFrame.

    Parameters:
    - data: The JSON response from the Google Trends API.

    Returns:
    - A pandas DataFrame with columns for location and extracted value (interest score).
    """
    if not data or data == "[]":
        logger.warning("Received empty or invalid data for Interest By Region")
        return []

    logger.info("Results from Google Trends API: Interest By Region")
    regions = data.get("interest_by_region", [])
    cleaned_data = []

    for region in regions:
        location = region.get("location", "")
        extracted_value = region.get("extracted_value", 0)

        cleaned_data.append({"Location": location, "Extracted Value": extracted_value})

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    return df


def filter_InterestOverTime(data):
    """
    Filters and transforms the interest over time data into a wide format DataFrame, including the timestamp.

    Parameters:
    - data: The JSON response from the Google Trends API.

    Returns:
    - A pandas DataFrame where each row is a date range, and each column is a query with the extracted value.
    """
    if not data or data == "[]":
        logger.warning("Received empty or invalid data for Interest Over Time")
        return []

    logger.info("Results from Google Trends API: Interest Over Time")
    timeline_data = data.get("interest_over_time", {}).get("timeline_data", [])
    cleaned_data = []

    for period in timeline_data:
        date_range = period.get("date", "")
        timestamp = period.get("timestamp", "")
        period_data = {"Date": date_range, "Timestamp": timestamp}

        for value in period.get("values", []):
            query = value.get("query", "")
            extracted_value = value.get("extracted_value", 0)
            period_data[query] = extracted_value

        cleaned_data.append(period_data)

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    return df


def filter_RelatedQueries(data):
    """
    Filters and transforms the related queries data into a structured DataFrame, excluding the link and SerpApi link.

    Parameters:
    - data: The JSON response from the Google Trends API.

    Returns:
    - A pandas DataFrame with columns for query, extracted value, and type.
    """
    if not data or data == "[]":
        logger.warning("Received empty or invalid data for Related Queries")
        return []

    logger.info("Results from Google Trends API: Related Queries")
    related_queries = data.get("related_queries", {})
    cleaned_data = []

    for query_type in ["rising", "top"]:
        queries = related_queries.get(query_type, [])
        for query in queries:
            cleaned_data.append(
                {
                    "Query": query.get("query", ""),
                    "Extracted Value": query.get("extracted_value", 0),
                    "Type": query_type,
                }
            )

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    return df


def filter_YouTubeSearch(data):
    """
    Filters and transforms the YouTube search data into a structured DataFrame.

    Parameters:
    - data: The JSON response from the YouTube Search API.

    Returns:
    - A pandas DataFrame with columns for title, views, published date, and description.
    """
    if not data or data == "[]":
        logger.warning("Received empty or invalid data for YouTube Search")
        return []

    logger.info("Results from YouTube Search API")
    video_results = data.get("video_results", [])
    cleaned_data = []

    for video in video_results:
        cleaned_data.append(
            {
                "Title": video.get("title", ""),
                "Views": video.get("views", 0),
                "Published Date": video.get("published_date", ""),
                "Description": video.get("description", ""),
            }
        )

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    return df


def filter_DiscussionsAndForums(data):
    """
    Filters and transforms the Discussions and Forums data into a structured DataFrame.

    Parameters:
    - data: The JSON response from the Discussions and Forums API.

    Returns:
    - A pandas DataFrame with columns for title, date, comments, and source.
    """
    if not data or data == "[]":
        logger.warning("Received empty or invalid data for Discussions and Forums")
        return []

    logger.info("Results from Discussions and Forums API")
    discussions = data.get("discussions_and_forums", [])
    cleaned_data = []

    for discussion in discussions:
        comments = next(
            (
                ext
                for ext in discussion.get("extensions", [])
                if "comments" in ext or "answers" in ext
            ),
            "",
        )

        cleaned_data.append(
            {
                "Title": discussion.get("title", ""),
                "Date": discussion.get("date", ""),
                "Comments": comments,
                "Source": discussion.get("source", ""),
            }
        )

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    return df


def filter_ShoppingResults(data):
    """
    Filters and transforms the Shopping Results data into a structured DataFrame.

    Parameters:
    - data: The JSON response from the Shopping Results API.

    Returns:
    - A pandas DataFrame with columns for title, price, rating, reviews, and source.
    """
    if not data or data == "[]":
        logger.warning("Received empty or invalid data for Shopping Results")
        return []

    logger.info("Results from Shopping Results API")
    shopping_results = data.get("shopping_results", [])
    cleaned_data = []

    for product in shopping_results:
        cleaned_data.append(
            {
                "Title": product.get("title", ""),
                "Price": product.get("price", ""),
                "Rating": product.get("rating", ""),
                "Reviews": product.get("reviews", ""),
                "Source": product.get("source", ""),
            }
        )

    if not cleaned_data:
        return []

    df = pd.DataFrame(cleaned_data)
    return df
