from pydantic import BaseModel, EmailStr, field_validator
from typing import Dict, Any, Optional


class AnalyzeResponse(BaseModel):
    success: bool
    message: str
    filename: str
    recipient: str
    summary_preview: Optional[str] = None
    data_stats: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
