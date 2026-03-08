from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident, IncidentStatus
from app.models.room import Room
from app.schemas.incident_schema import IncidentCreate, IncidentUpdate, IncidentResponse

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident: IncidentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new incident report.
    
    Args:
        incident: Incident creation data
        
    Returns:
        IncidentResponse: Created incident details
        
    Raises:
        HTTPException: 404 if room not found
    """
    # Check if room exists
    room = db.query(Room).filter(Room.id == incident.room_id).first()
    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Room with id {incident.room_id} not found"
        )
    
    # Create incident with REPORTED status
    db_incident = Incident(
        **incident.model_dump(),
        status=IncidentStatus.REPORTED
    )
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)
    return db_incident


@router.get("", response_model=list[IncidentResponse])
async def list_incidents(
    status: IncidentStatus = None,
    db: Session = Depends(get_db)
):
    """
    Get all incidents with optional filtering by status.
    
    Args:
        status: Filter by status (optional)
        
    Returns:
        list: List of incidents
    """
    query = db.query(Incident)
    
    if status:
        query = query.filter(Incident.status == status)
    
    return query.all()


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific incident by ID.
    
    Args:
        incident_id: ID of the incident
        
    Returns:
        IncidentResponse: Incident details
        
    Raises:
        HTTPException: 404 if incident not found
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id {incident_id} not found"
        )
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse)
async def update_incident(
    incident_id: int,
    incident_update: IncidentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an incident report. Can only update description and equipment.
    
    Args:
        incident_id: ID of the incident to update
        incident_update: Updated incident data
        
    Returns:
        IncidentResponse: Updated incident details
        
    Raises:
        HTTPException: 404 if incident not found
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id {incident_id} not found"
        )
    
    update_data = incident_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(incident, key, value)
    
    db.commit()
    db.refresh(incident)
    return incident


@router.put("/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark an incident as resolved.
    
    Args:
        incident_id: ID of the incident to resolve
        
    Returns:
        IncidentResponse: Updated incident details
        
    Raises:
        HTTPException: 404 if incident not found
        HTTPException: 400 if incident is already resolved
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id {incident_id} not found"
        )
    
    if incident.status == IncidentStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Incident is already resolved"
        )
    
    incident.status = IncidentStatus.RESOLVED
    db.commit()
    db.refresh(incident)
    return incident


@router.delete("/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an incident report.
    
    Args:
        incident_id: ID of the incident to delete
        
    Raises:
        HTTPException: 404 if incident not found
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id {incident_id} not found"
        )
    
    db.delete(incident)
    db.commit()
