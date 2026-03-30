"""
Pydantic schemas for analysis requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AnalysisRequest(BaseModel):
    """Schema for analysis request"""
    headline: str = Field(..., min_length=1, max_length=1000)
    image_url: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "headline": "Breaking: Scientists discover cure for disease",
                "image_url": "https://example.com/image.jpg"
            }
        }


class FactCheck(BaseModel):
    """Schema for fact-check reference"""
    title: str
    url: str
    claim_reviewed: str
    rating: str


class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    id: str = Field(..., alias="_id")
    headline: str
    image_url: Optional[str] = None
    prediction: str = Field(..., description="Fake, Real, or Misleading")
    confidence: float = Field(..., ge=0.0, le=1.0)
    similarity: Optional[float] = Field(None, ge=0.0, le=1.0)
    explanation: str
    fact_checks: List[FactCheck] = []
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "headline": "Breaking: Scientists discover cure for disease",
                "image_url": "https://example.com/image.jpg",
                "prediction": "Misleading",
                "confidence": 0.85,
                "similarity": 0.42,
                "explanation": "The claim is partially true but lacks scientific evidence",
                "fact_checks": [
                    {
                        "title": "Fact Check Title",
                        "url": "https://factcheck.org/article",
                        "claim_reviewed": "Scientists discover cure",
                        "rating": "Mostly False"
                    }
                ],
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class AnalysisHistoryResponse(BaseModel):
    """Schema for history list response"""
    total: int
    page: int
    limit: int
    items: List[AnalysisResponse]


class DeleteResponse(BaseModel):
    """Schema for delete response"""
    success: bool
    message: str


class AnalyticsResponse(BaseModel):
    """Schema for analytics data"""
    total_analyses: int
    fake_count: int
    real_count: int
    misleading_count: int
    average_confidence: float
    predictions_by_date: dict
    top_headlines: List[str]
