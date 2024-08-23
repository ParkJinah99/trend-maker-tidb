from src.utils.openai.init_openai import init_openai_llm
from src.utils.openai.prompts import (
    STRATEGY_GENERATOR_PROMPT,
    TREND_SUMMARY_GENERATOR_PROMPT,
    SLOGAN_GENERATOR_PROMPT,
    COLOR_PALETTE_GENERATOR_PROMPT,
)
from src.utils.openai.strategy_creator.models import (
    StrategyMetadata,
    SummaryMetadata,
    ColorPalettes,
)
from src.utils.openai.strategy_creator.generate_logo import generate_logo_image

from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
import json
from collections import defaultdict


from src.database.init_tidb import init_tidb
from src.database import TiDBHandler
from src.database.strategies import vector_search_brand
from src.config import logger

llm = init_openai_llm()
db = init_tidb()


def create_general_strategy(
    business_query: str, trending_keywords: list, given_data
) -> dict:
    logger.info(f"[OpenAI] Generate Strategy with business query: {business_query}")
    data = process_data_for_llm(given_data)

    parser = PydanticOutputParser(pydantic_object=StrategyMetadata)

    prompt = PromptTemplate(
        template=STRATEGY_GENERATOR_PROMPT,
        input_variables=["business_query", "trending_keywords", "data"],  # TODO
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    # Set up a parser and generate output
    llm_chain = prompt | llm
    output = llm_chain.invoke(
        {
            "business_query": business_query,
            "trending_keywords": trending_keywords,
            "data": data,
        }
    )
    strategy = parser.invoke(output)
    trend_summary = generate_trend_summary(data)

    strategy_metadata = strategy.dict()
    strategy_metadata["trend_summary"] = trend_summary
    return strategy_metadata


def create_brand_identities(strategies_metadata: dict, db: TiDBHandler) -> dict:
    logger.info(
        f"[OpenAI] Create brand identitites with strategies data: {strategies_metadata}"
    )
    brand_identities = vector_search_brand(strategies_metadata, db)
    slogan_list = brand_identities.get("slogans", [])

    # Convert colors to RGB format
    color_palette_list = [
        [
            rgb_to_hex(json.loads(color["rgb"])[i : i + 3])
            for i in range(0, len(json.loads(color["rgb"])), 3)
        ]
        for color in brand_identities.get("colors", [])
    ]

    # Generate color palette using LLM
    color_palette_list = generate_color_palette(strategies_metadata, color_palette_list)

    # Generate slogan using LLM
    slogan = generate_slogan(
        strategies_metadata["brand_name"],
        strategies_metadata["target_audience"],
        strategies_metadata["brand_description"],
        slogan_list,
    )

    # Generate logo image using DALL-E
    brand_name_description = f"The brand name is {strategies_metadata['brand_name']}"
    brand_description_description = (
        f"The brand description is {strategies_metadata['brand_description']}"
    )
    color_pallete_description = f"Try to use colors from: {color_palette_list}"
    logo_description = f"{brand_name_description}. {brand_description_description}. {color_pallete_description}"
    logo_image = generate_logo_image(logo_description)

    return {
        "brand_slogan": slogan,
        "brand_color_palette": color_palette_list,
        "logo_image": brand_identities.get("logos"),
        "brand_logo": logo_image,
    }


def process_data_for_llm(data: dict) -> dict:
    logger.info(f"[OpenAI] Process data for llm: {data}")
    processed_data = {}
    top_regions = {}
    time_trends = {}
    top_related_queries = []
    top_videos = []
    top_products = []

    if data.get("ComparativeBreakdownByRegion"):
        top_regions = defaultdict(list)
        for region in data["ComparedBreakdownByRegion"]:
            location = region["Location"]
            for query in data["queries"]:
                if region[query] > 0:
                    top_regions[query].append((location, region[query]))
        for query, regions in top_regions.items():
            sorted_query = sorted(regions, key=lambda x: x[1], reverse=True)
            if len(sorted_query) > 2:
                top_regions[query] = sorted_query[:2]
            else:
                top_regions[query] = sorted_query

    if data.get("InterestOverTime"):
        time_trends = {}
        for query, trends in data["InterestOverTime"].items():
            if len(trends) > 0:
                sorted_trends = sorted(trends.items(), key=lambda x: x[1], reverse=True)
                peak_time = sorted_trends[0][0]
                peak_value = sorted_trends[0][1]
                time_trends[query] = {
                    "peak_time": peak_time,
                    "peak_value": peak_value,
                    "recent_value": list(trends.values())[-1],
                }
    if data.get("RelatedQueries"):
        # Process RelatedQueries to get the top queries
        related_queries = []
        for key, query in data["RelatedQueries"]["Query"].items():
            value = data["RelatedQueries"]["Extracted Value"][key]
            related_queries.append((query, value))

        # Sort the queries by their extracted value in descending order
        sorted_queries = sorted(related_queries, key=lambda x: x[1], reverse=True)

        # Get the top 5 related queries
        if len(sorted_queries) > 5:
            top_related_queries = sorted_queries[:5]
        else:
            top_related_queries = sorted_queries

    if data.get("YouTubeSearch"):
        youtube_videos = []
        for key, title in data["YouTubeSearch"]["Title"].items():
            trend_score = data["YouTubeSearch"]["trend_score"][key]
            youtube_videos.append((title, trend_score))

        # Sort the videos by their trend score in descending order
        sorted_videos = sorted(youtube_videos, key=lambda x: x[1], reverse=True)

        # Get the top 3 videos based on trend score
        if len(sorted_videos) > 3:
            top_videos = sorted_videos[:3]
        else:
            top_videos = sorted_videos
    if data.get("ShoppingResults"):
        shopping_products = []
        for key, title in data["ShoppingResults"]["Title"].items():
            trend_score = data["ShoppingResults"]["Trend Score"][key]
            shopping_products.append((title, trend_score))

        # Sort the products by their trend score in descending order
        sorted_products = sorted(shopping_products, key=lambda x: x[1], reverse=True)

        # Get the top 3 products based on trend score
        if len(sorted_products) > 3:
            top_products = sorted_products[:3]
        else:
            top_products = sorted_products

    processed_data = {
        "top_regions": top_regions,
        "time_trends": time_trends,
        "related_queries": top_related_queries,
        "top_youtube_videos": top_videos,
        "top_shopping_products": top_products,
    }

    return processed_data


def generate_trend_summary(processed_data: dict) -> dict:
    logger.info(
        f"[OpenAI] Generate trend summary data with processed data: {processed_data}"
    )
    parser = PydanticOutputParser(pydantic_object=SummaryMetadata)

    prompt = PromptTemplate(
        template=TREND_SUMMARY_GENERATOR_PROMPT,
        input_variables=["data"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm_chain = prompt | llm
    output = llm_chain.invoke({"data": processed_data})

    return parser.invoke(output).trend_summary


def generate_color_palette(strategies_metadata: dict, color_palette_list: list) -> list:
    logger.info(
        f"[OpenAI] Generate color palette with strategies data: {strategies_metadata}, {color_palette_list}"
    )
    parser = PydanticOutputParser(pydantic_object=ColorPalettes)

    prompt = PromptTemplate(
        template=COLOR_PALETTE_GENERATOR_PROMPT,
        input_variables=["competitor_color_palettes", "brand_description"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm_chain = prompt | llm
    output = llm_chain.invoke(
        {
            "competitor_color_palettes": color_palette_list,
            "brand_description": strategies_metadata["brand_description"],
        }
    )

    return parser.invoke(output).color_palettes


def generate_slogan(
    brand_name: str, target_audience: str, brand_description: str, slogans: list
) -> str:
    logger.info(
        f"[OpenAI] Generate slogan with brand data: {brand_name}, {brand_description} "
    )
    prompt = PromptTemplate(
        template=SLOGAN_GENERATOR_PROMPT,
        input_variables=[
            "brand_name",
            "target_audience",
            "brand_description",
            "slogans",
        ],
    )

    llm_chain = prompt | llm
    output = llm_chain.invoke(
        {
            "brand_name": brand_name,
            "target_audience": target_audience,
            "brand_description": brand_description,
            "slogans": slogans,
        }
    )

    return output.content


def rgb_to_hex(rgb: list) -> str:
    return "#{:02X}{:02X}{:02X}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
