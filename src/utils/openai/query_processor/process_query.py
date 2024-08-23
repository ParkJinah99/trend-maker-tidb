from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from src.utils.openai.init_openai import init_openai_llm
from src.utils.openai.prompts import KEYWORD_GENERATOR_PROMPT
from src.utils.openai.query_processor.models import QueryMetadata

from src.config import logger  # Import the logger

llm = init_openai_llm()


def process_query(text: str) -> QueryMetadata:
    logger.info(f"[OpenAI] Process the query: {text}")

    parser = PydanticOutputParser(pydantic_object=QueryMetadata)

    prompt = PromptTemplate(
        template=KEYWORD_GENERATOR_PROMPT,
        input_variables=["business_scope"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm_chain = prompt | llm
    output = llm_chain.invoke({"business_scope": text})
    query_metadata = parser.invoke(output)

    return {"name": query_metadata.name, "keywords": query_metadata.keywords}
