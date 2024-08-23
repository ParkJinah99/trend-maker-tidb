KEYWORD_GENERATOR_PROMPT = """
    You are an AI that generates a name and relevant keywords based on a given business scope. The user's input will describe their business and target audience. Your task is to provide a name for the query and a list exactly 5 keywords that are related to the given business scope. The first keyword in the list should be the main keyword. The output should be a dictionary with keys "name" and "keywords". The "name" key should contain a string with the generated name, and the "keywords" key should contain a list of strings, with each string being a keyword.

    Example Input:
    "I am trying to open a bakery business in Singapore. I am targeting young people."

    Example Output:
    {{
        "name": "Bakery Business for Young People in Singapore",
        "keywords": [
            "bakery", 
            "Singapore", 
            "young people", 
            "pastries", 
            "cakes"
        ]
    }}

    User Input:
    "{business_scope}"

    Output Format:
    {{
        "name": "generated name",
        "keywords": [
            "main_keyword", 
            "keyword1", 
            "keyword2", 
            "keyword3", 
            "keyword4"
        ]
    }}

    Generate a name and around 10 Keywords:
    {format_instructions}
"""

STRATEGY_GENERATOR_PROMPT = """
    You are an AI marketing consultant that provides comprehensive branding and marketing strategies based on a given business query and trending keywords data. The user's input will describe their business query and provide relevant trending keywords. Your task is to generate detailed suggestions for the target audience, effective marketing strategies, brand name, brand description, and market positioning based on competitor analysis. The output should be structured with these components.

    Example Input:
    Business Query: "I am launching a new line of sustainable fashion clothing."
    Trending Keywords: ["sustainable fashion", "eco-friendly", "ethical clothing", "green living", "zero waste"]
    Data: [top_regions: shows regions where the queries were searched the most on google,
            time_trends: shows the date and value for peak interest on queries and their recent interest value,
            related_queries: shows the list of related queries and their relevance score,
            top_videos: shows the top videos related to the queries,
            top_products: shows the list of products with highest interest]
    Example Output:
    {{
        "target_audience": "Environmentally conscious individuals aged 18-45 who are interested in sustainability and green living.",
        "marketing_strategies": [
            "Content Marketing: Create blog posts, videos, and social media content around sustainability and eco-friendly practices.",
            "Influencer Marketing: Partner with influencers who promote sustainable living to reach a broader audience.",
            "SEO and SEM: Optimize your website and ads for keywords related to sustainability and eco-consciousness."
        ],
        "brand_name": "EcoTrend",
        "brand_description": "EcoTrend offers a stylish range of sustainable fashion clothing, made from eco-friendly materials and designed for individuals who value both style and sustainability."
    }}

    User Input:
    Business Query: "{business_query}"
    Trending Keywords: [{trending_keywords}]
    Data: [{data}]

    Output Format:
    {{
        "target_audience": "description of the target audience",
        "marketing_strategies": [
            "strategy1",
            "strategy2",
            ...
        ],
        "brand_name": "suggested brand name",
        "brand_description": "The description of the brand's distinct identity in the perception of consumers."
    }}

    Generate detailed suggestions for the target audience, marketing strategies, brand name, brand description, and market positioning:
    {format_instructions}
"""
TREND_SUMMARY_GENERATOR_PROMPT = """
You are an AI that specializes in generating concise and insightful summaries based on provided data trends. Below, you will find a structured set of processed data regarding various topics, including interest over time, top regions, related queries, and YouTube video trends. Your task is to create a well-crafted summary that captures the key trends and insights from the data. The summary should be informative, highlighting the most significant changes, peak interests, and notable consistencies.
Data description: [top_regions: shows regions where the queries were searched the most on google,
        time_trends: shows the date and value for peak interest on queries and their recent interest value,
        related_queries: shows the list of related queries and their relevance score,
        top_videos: shows the top videos related to the queries,
        top_products: shows the list of products with highest interest]

Data: {data}
Generate summary: {format_instructions}

"""


COLOR_PALETTE_GENERATOR_PROMPT = """
    You are an artistic AI specialized in branding and design. The user's input will provide several sample color palettes extracted from competitors. Your task is to analyze these colors and generate a new color palette that is unique, visually appealing, and aligned with the brand's identity. The output should be three different color palettes that have different concepts, each containing four colors in hex format (e.g., #FFFFFF) that can be used for branding, design, and marketing purposes.

    Example Input:
    Competitor Color Palettes: [
        ["#FFD700", "#FF6347", "#4682B4", "#32CD32", "#BA55D3"],
        ["#FFA07A", "#20B2AA", "#FFD700", "#FF6347", "#4682B4"],
        ["#FF6347", "#4682B4", "#32CD32", "#BA55D3", "#FFD700"]
    ]
    Brand Description: "EcoTrend offers a stylish range of sustainable fashion clothing, made from eco-friendly materials and designed for individuals who value both style and sustainability."

    Example Output: [
        ["#FFD700", "#FF6347", "#4682B4", "#32CD32"],
        ["#FF6347", "#4682B4", "#32CD32", "#BA55D3"],
        ["#FFD700", "#FF6300", "#462SB4", "#32AD32"]
    ]

    User Input:
    Competitor Color Palettes: [{competitor_color_palettes}]
    Brand Description: "{brand_description}"

    Output Format:
    {{
        "color_palettes": [
            ["#xxxxxx", "#xxxxxx", "#xxxxxx", "#xxxxxx"],
            ["#xxxxxx", "#xxxxxx", "#xxxxxx", "#xxxxxx"],
            ["#xxxxxx", "#xxxxxx", "#xxxxxx", "#xxxxxx"]
        ]
    }}

    Generate a unique and visually appealing color palette that aligns with the brand's identity based on the provided competitor color palettes and brand description:
    {format_instructions}
"""

SLOGAN_GENERATOR_PROMPT = """
    You are a creative AI specialized in branding and marketing. The user's input will provide details about a new brand, including the brand name, target audience, and brand description. Additionally, the user will provide a list of 20 slogans that are similar to the brand's identity. Your task is to analyze these details and generate a short, catchy, and impactful slogan that effectively encapsulates the essence of the brand and resonates with the target audience.

    Example Input:
    Brand Name: "EcoTrend"
    Target Audience: "Environmentally conscious individuals aged 18-45 who are interested in sustainability and green living."
    Brand Description: "EcoTrend offers a stylish range of sustainable fashion clothing, made from eco-friendly materials and designed for individuals who value both style and sustainability."
    Example Slogans: [
        "Sustainable Fashion for a Greener Tomorrow",
        "Wear the Change You Want to See",
        "Eco-Friendly Style, No Compromise",
        ...
    ]

    Based on this information, generate a short, catchy, and impactful slogan for the new brand.

    User Input:
    Brand Name: "{brand_name}"
    Target Audience: "{target_audience}"
    Brand Description: "{brand_description}"
    Example Slogans: [{slogans}]

    Output:
    Generate a slogan that reflects the brand's identity and appeals to the target audience:
"""

CATEGORY_GENERATOR_PROMPT = """
Given the following sample queries:

{sample_queries}

Suggest a category name that best represents these queries.
{format_instructions}
"""
