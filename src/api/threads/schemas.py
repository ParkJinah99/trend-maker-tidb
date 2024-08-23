from pydantic import BaseModel


class QueryRequest(BaseModel):
    user_id: int
    user_query: str
    country: str
