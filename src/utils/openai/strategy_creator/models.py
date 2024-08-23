from pydantic import BaseModel, Field, field_validator
from typing import List


class StrategyMetadata(BaseModel):
    target_audience: str = Field(description="Description of the target audience")
    marketing_strategies: List[str] = Field(
        description="A list of effective marketing strategies"
    )
    brand_name: str = Field(description="Suggested brand name")
    brand_description: str = Field(
        description="The description of the brand's distinct identity in the perception of consumers."
    )

    @field_validator("marketing_strategies", mode="before")
    def validate_marketing_strategies(cls, v):
        if not isinstance(v, list) or not all(isinstance(i, str) for i in v):
            raise ValueError("Must be a list of strings")
        if len(v) < 1:
            raise ValueError("List cannot be empty")
        return v

    @field_validator(
        "target_audience",
        "brand_name",
        "brand_description",
        mode="before",
    )
    def validate_non_empty_string(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("This field must be a non-empty string")
        return v


class SummaryMetadata(BaseModel):
    trend_summary: str = Field(
        description="Summary of the provided focused on current trends related to the business query."
    )


class ColorPalettes(BaseModel):
    color_palettes: List[List[str]]
