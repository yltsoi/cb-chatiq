from typing import Optional

from pydantic import BaseModel, Field

class AutoCompleteRequest(BaseModel):
    query: str = Field(min_length=3, max_length=4096)
    max_result_count: int = Field(min=1, max=10)

class ChatIQRequest(BaseModel):
    question: str = Field(min_lenth=3, max_length=4096)
    rqu_id: str = ""
    offset: int = Field(default=0)

class ChatIQRequestStream(BaseModel):
    question: str = Field(min_lenth=3, max_length=4096)
    rqu_id: str = ""
    processed_chunk: int = Field(default=0)

class LLMRequest(BaseModel):
    prompt: str = ""

class TokenPayload(BaseModel):
    token: str = Field(min_length=3, max_length=4096)

class UserToken(BaseModel):
    username: str = ""
    password: str = ""


class QlikQuery(BaseModel):
    question: str = Field(min_lenth=3, max_length=4096)
    numberOfRequest: int = Field(default=10)
    minEmployees: int = Field(default=-1)
    maxEmployees: int = Field(default=-1)
    minRevenue:  int = Field(default=-1)
    maxRevenue:  int = Field(default=-1)
    relevancyThreshod:  int = Field(default=0)

    isParentCompany: str = ""
    naicsCode: list = []
    investorType: list = []
    investorNames: list = []
    relationshipStatus: str = ""




