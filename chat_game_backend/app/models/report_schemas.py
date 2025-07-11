# app/models/report_schemas.py

from pydantic import BaseModel, Field
from typing import Optional


class ReportRequest(BaseModel):
    offender: str = Field(..., min_length=3, max_length=30)
    reason: str = Field(..., min_length=10, max_length=500)


class ReportEntry(BaseModel):
    reporter: str
    offender: str
    reason: str
    timestamp: float
