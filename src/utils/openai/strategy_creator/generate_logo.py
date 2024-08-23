import requests
from src.utils.openai.init_openai import init_openai_client
import base64
import json
from src.config import logger

client = init_openai_client()


def generate_logo_image(logo_description: str) -> dict:
    """
    Generate a logo image using the DALL-E image generation tool.

    Args:
        logo_description (str): The description of the logo.

    Returns:
        dict: The response from the DALL-E image generation tool.
    """
    logger.info(
        f"[OpenAI] Generate logo image with logo description: {logo_description}"
    )

    prefix = "Create a simple and minimalist Vector logo design of a brand with the following description and requirements:"
    response = client.images.generate(
        model="dall-e-3",
        prompt=prefix + logo_description,
        n=1,
        size="1024x1024",
        response_format="url",
    )
    image_url = response.data[0].url
    print(image_url)
    logo_image = requests.get(image_url).content

    logo_image_base64 = base64.b64encode(logo_image).decode("utf-8")
    # logo_image_json = json.dumps(logo_image_base64)

    return logo_image_base64
