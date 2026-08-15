from pydantic import BaseModel, Field


class SupportRequest(BaseModel):
    subject: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=10, max_length=5000)