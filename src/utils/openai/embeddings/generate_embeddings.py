from src.utils.openai.init_openai import init_openai_embeddings

embeddings_model = init_openai_embeddings()


def get_embeddings(text: str):
    """
    Get embeddings for the input text.

    Args:
        text (str): The input text.

    Returns:
        Dict: The embeddings for the input text.
    """
    text = text.replace("\n", " ")
    embeeded_text = embeddings_model.embed_query(text)

    return embeeded_text
