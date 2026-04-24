from pydantic import BaseModel

class QueryIntentOutput(BaseModel):
    intent: str
    useEmbedding: bool