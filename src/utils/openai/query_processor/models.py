from pydantic import BaseModel, Field, field_validator


# Define your desired data structure
class QueryMetadata(BaseModel):
    name: str = Field(description="The generated name for the query")
    keywords: list[str] = Field(description="A list of relevant keywords")

    # Custom validation logic
    @field_validator("keywords")
    def check_keywords_length(cls, v):
        if not isinstance(v, list) or not all(isinstance(i, str) for i in v):
            raise ValueError("Keywords must be a list of strings")
        if len(v) < 1:
            raise ValueError("Keywords list cannot be empty")
        return v

    @field_validator("name")
    def check_name_length(cls, v):
        if not isinstance(v, str) or len(v) < 1:
            raise ValueError("Name must be a non-empty string")
        return v
