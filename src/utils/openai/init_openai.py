from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.config import OPENAI_CREDENTIAL
from openai import OpenAI


def init_openai_llm() -> ChatOpenAI:
    """
    Initialize the OpenAI Chat model.

    Returns:
        ChatOpenAI: An instance of the OpenAI Chat model.
    """
    llm = ChatOpenAI(
        api_key=OPENAI_CREDENTIAL["OPENAI_API_KEY"],
        model_name="gpt-4o",
    )
    return llm


def init_openai_embeddings() -> OpenAIEmbeddings:
    """
    Initialize the OpenAI Embeddings model.

    Returns:
        OpenAIEmbeddings: An instance of the OpenAI Embeddings model.
    """
    embeddings_model = OpenAIEmbeddings(
        api_key=OPENAI_CREDENTIAL["OPENAI_API_KEY"], model="text-embedding-3-small"
    )
    return embeddings_model


def init_openai_client() -> OpenAI:
    """
    Initialize the OpenAI client.

    Returns:
        OpenAi: An instance of the OpenAI client.
    """
    client = OpenAI(api_key=OPENAI_CREDENTIAL["OPENAI_API_KEY"])
    return client
