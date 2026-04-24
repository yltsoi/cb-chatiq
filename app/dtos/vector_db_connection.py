from pydantic import BaseModel, Field
from typing import Union, Optional, Dict
from typing_extensions import Literal

CONFIRMATION_MSG = Literal["I confirm the removal of this object"]

class VectorDbConnection:
    def __init__(self):
        pass

class Confirmation(BaseModel):
    confirmation: CONFIRMATION_MSG

class SQSData(BaseModel):
    url: str
    receipt: Union[str, None] = None
    confirmation: Confirmation

class OSQuery(BaseModel):
    os_query: DIct = Field(example={"query": {"match" : {"title": "wind"}}, "size": 1, "sort": [{"price": {"order": "asc"}}]})
    index_name: Optional[str] = None

