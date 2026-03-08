from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from datetime import datetime
from app.database import Base
import enum


class IncidentStatus(str, enum.Enum):
    """Incident status enumeration"""
    REPORTED = "reported"
    ANALYZED = "analyzed"
    RESOLVED = "resolved"


class Incident(Base):
    """
    Incident model for reporting facility issues.
    These incidents will be processed by an AI agent for analysis.
    
    Attributes:
        id: Unique identifier for the incident
        room_id: ID of the room where incident occurred (foreign key)
        reporter_id: ID of the user reporting the incident
        description: Detailed description of the incident
        equipment: Equipment or facility involved in the incident
        status: Current status (reported, analyzed, resolved)
        created_at: Timestamp when incident was reported
    """
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False, index=True)
    reporter_id = Column(Integer, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    equipment = Column(String(100), nullable=False)
    status = Column(Enum(IncidentStatus), default=IncidentStatus.REPORTED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Incident(id={self.id}, room_id={self.room_id}, status={self.status}, created_at={self.created_at})>"
