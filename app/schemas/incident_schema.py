from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.incident import IncidentStatus


class IncidentCreate(BaseModel):
    """Schema for creating a new incident report"""
    room_id: int = Field(..., gt=0)
    reporter_id: int = Field(..., gt=0)
    description: str = Field(..., min_length=1, max_length=500)
    equipment: str = Field(..., min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "room_id": 1,
                "reporter_id": 789,
                "description": "Broken projector in classroom",
                "equipment": "Projector"
            }
        }


class IncidentUpdate(BaseModel):
    """Schema for updating incident information"""
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    equipment: Optional[str] = Field(None, min_length=1, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Updated incident description"
            }
        }


class IncidentResponse(BaseModel):
    """Schema for incident response"""
    id: int
    room_id: int
    reporter_id: int
    description: str
    equipment: str
    status: IncidentStatus
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "room_id": 1,
                "reporter_id": 789,
                "description": "Broken projector in classroom",
                "equipment": "Projector",
                "status": "reported",
                "created_at": "2024-03-08T10:30:00"
            }
        }
