from typing import Literal

from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=5000)


class TriageResult(BaseModel):
    category: Literal["technical", "billing", "account", "other"]
    priority: Literal["low", "medium", "high", "urgent"]
    summary: str = Field(min_length=10, max_length=500)
    next_action: str = Field(min_length=5, max_length=500)
    draft_response: str = Field(min_length=10, max_length=2000)