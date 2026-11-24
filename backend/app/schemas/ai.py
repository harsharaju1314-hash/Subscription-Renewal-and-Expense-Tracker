from typing import List, Optional
from datetime import date
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    id: int
    name: str
    cost: float
    billing_cycle: str
    category: str
    renewal_date: Optional[str] = None
    relevance_score: Optional[float] = None


class AIChatRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000)
    conversation_id: Optional[int] = None


class AIChatResponse(BaseModel):
    answer: str
    conversation_id: Optional[int] = None
    sources: List[SourceReference] = []
    latency_ms: int = 0
    tokens_used: int = 0
    model: str = "rag-grounded-gpt4o-mini"
    timestamp: str


class AISummarizeResponse(BaseModel):
    summary: str
    highlights: List[str]
    monthly_total: float
    annual_projection: float
    recommendations: List[str]
