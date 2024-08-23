from src.config import SERPAPI_CREDENTIAL
from src.utils.data_generator.data_filters import (
    filter_ComparedBreakdownByRegion,
    filter_InterestByRegion,
    filter_InterestOverTime,
    filter_RelatedQueries,
    filter_YouTubeSearch,
    filter_ShoppingResults,
)

from serpapi import GoogleSearch
from src.config import logger  # Import the logger


def get_all_data(
    keywords,
    geo="",
    region="COUNTRY",
    tz=420,
    frequency="daily",
    hl="en",
    gl="us",
    cat="all",
    device="mobile",
    sort_by="relevance",
):
    """
    Calls all API functions with the provided parameters and returns a dictionary with the results.

    Parameters:
    - keywords: A string of 5 comma-separated keywords.
    - geo: Geolocation.
    - region: Region for more specific results.
    - tz: Timezone offset.
    - frequency: Frequency for trending now API.
    - hl: Language parameter.
    - gl: Country code for geolocation.
    - device: Device type (mobile/PC).
    - sort_by: Sorting criteria for shopping results.

    Returns:
    - A dictionary with the results from all the API calls.
    """

    queries_used = {
        "q": keywords,
        "geo": geo,
        "region": region,
        "tz": tz,
        "frequency": frequency,
        "hl": hl,
        "gl": gl,
        "cat": cat,
        "device": device,
        "sort_by": sort_by,
    }

    # Split the keywords into a list for APIs that don't accept multiple queries
    keyword_list = keywords.split(",")

    data = {
        "ComparedBreakdownByRegion": get_Trends_ComparedBreakdownByRegion(
            keywords, geo, region
        ),
        "InterestByRegion": get_Trends_InterestByRegion(
            keyword_list[0], geo, region
        ),  # search for the main keyword only
        "InterestOverTime": get_Trends_InterestOverTime(keywords, geo),
        "RelatedQueries": get_Trends_RelatedQueries(
            keyword_list[0], tz
        ),  # search for the main keyword only
        "YouTubeSearch": get_YouTube_Search(
            keyword_list[0], gl, hl
        ),  # for the main keyword only
        "ShoppingResults": get_ShoppingResults(
            keyword_list[0], geo, hl, gl, device, sort_by
        ),  # search for the main keyword only
    }

    return queries_used, data


# Google Trends API: Compared Breakdown By Region
def get_Trends_ComparedBreakdownByRegion(q, geo="", region="COUNTRY", tz=420):
    """
    Fetches the Google Trends data for Compared Breakdown By Region and filters it.

    Parameters:
    - q: Keywords searched, comma-separated for multiple queries.
    - geo: Location (default is 'US').
    - region: Specific region for more refined results (default is 'COUNTRY').
    - tz: Timezone offset (default is 420 for PDT).

    Returns:
    - Filtered DataFrame.
    """
    params = {
        "engine": "google_trends",
        "q": q,
        "region": region,
        "data_type": "GEO_MAP",
        "api_key": SERPAPI_CREDENTIAL,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if results != "[]":
        return filter_ComparedBreakdownByRegion(results)
    return None


# Google Trends API: Interest By Region
def get_Trends_InterestByRegion(q, geo="", region="COUNTRY"):
    """
    Fetches the Google Trends data for Interest By Region and filters it.

    Parameters:
    - q: Keywords searched, one at a time.
    - geo: Location (default is 'US').
    - region: Specific region for more refined results (default is 'COUNTRY').
    - region: if region is 'CITY' then geo should be the country code.)

    Returns:
    - Filtered DataFrame.
    """
    if region == "COUNTRY":
        params = {
            "engine": "google_trends",
            "q": q,
            "data_type": "GEO_MAP_0",
            "api_key": SERPAPI_CREDENTIAL,
        }

    else:
        params = {
            "engine": "google_trends",
            "q": q,
            "geo": geo,
            "region": region,
            "data_type": "GEO_MAP_0",
            "api_key": SERPAPI_CREDENTIAL,
        }

    search = GoogleSearch(params)
    results = search.get_dict()
    if results != "[]":
        return filter_InterestByRegion(results)
    else:
        params = {
            "engine": "google_trends",
            "q": q,
            "region": "COUNTRY",
            "data_type": "GEO_MAP_0",
            "api_key": SERPAPI_CREDENTIAL,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        if results != "[]":
            return filter_InterestByRegion(results)
        return None


# Google Trends API: Interest Over Time
def get_Trends_InterestOverTime(q, geo="", tz=420):
    """
    Fetches the Google Trends data for Interest Over Time and filters it.

    Parameters:
    - q: Keywords searched.
    - geo: Location (default is 'US').
    - tz: Timezone offset (default is 420 for PDT).

    Returns:
    - Filtered DataFrame.
    """
    params = {
        "engine": "google_trends",
        "q": q,
        "geo": geo,
        "data_type": "TIMESERIES",
        "tz": tz,
        "api_key": SERPAPI_CREDENTIAL,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if results != "[]":
        return filter_InterestOverTime(results)
    return None


# Google Trends API: Related Queries
def get_Trends_RelatedQueries(q, tz=420):
    """
    Fetches the Google Trends data for Related Queries and filters it.

    Parameters:
    - q: Keywords searched.
    - tz: Timezone offset (default is 420 for PDT).

    Returns:
    - Filtered DataFrame.
    """
    params = {
        "engine": "google_trends",
        "q": q,
        "data_type": "RELATED_QUERIES",
        "tz": tz,
        "api_key": SERPAPI_CREDENTIAL,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if results != "[]":
        return filter_RelatedQueries(results)
    return None


# YouTube Search API
def get_YouTube_Search(
    search_query, gl="US", hl="en", max_results=10, order="relevance"
):
    """
    Fetches data from the YouTube Search API with results filtered to those uploaded within the past year and filters it.

    Parameters:
    - search_query: The search term or phrase.
    - gl: Country code for geolocation (default is 'US').
    - hl: Language code (default is 'en').
    - max_results: Limit the number of results returned (default is 10).
    - order: Sort the results by relevance, date, etc. (default is 'relevance').

    Returns:
    - Filtered DataFrame.
    """
    params = {
        "engine": "youtube",
        "search_query": search_query,
        "gl": gl,
        "hl": hl,
        "max_results": max_results,
        "order": order,
        "sp": "EgQIBRAB",  # Filter to videos uploaded within the past year
        "api_key": SERPAPI_CREDENTIAL,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if results != "[]":
        return filter_YouTubeSearch(results)
    return None


# Google Shopping API: Shopping Results
def get_ShoppingResults(
    q, geo="US", hl="en", gl="us", device="mobile", sort_by="relevance"
):
    """
    Fetches data from the Google Shopping API for Shopping Results and filters it.

    Parameters:
    - q: The keyword being searched.
    - geo: Location of interest (default is 'US').
    - hl: Language filter (default is 'en').
    - gl: Country code for geolocation (default is 'us').
    - device: Specify if the search is on mobile or PC (default is 'mobile').
    - sort_by: Sort results by price, relevance, or reviews (default is 'relevance').

    Returns:
    - Filtered DataFrame.
    """
    params = {
        "engine": "google_shopping",
        "q": q,
        "geo": geo,
        "hl": hl,
        "gl": gl,
        "device": device,
        "sort_by": sort_by,
        "api_key": SERPAPI_CREDENTIAL,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    if results != "[]":
        return filter_ShoppingResults(results)
    return None
