from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone
from backend.app.database import get_db
from backend.app.models.entities import Blacklist, AuditLog
from backend.app.schemas.schemas import BlacklistResponse, BlacklistCreate
from backend.app.security import verify_api_key

router = APIRouter(prefix="/blacklist", tags=["Police Blacklist"])

@router.get("", response_model=List[BlacklistResponse])
def get_blacklist(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Returns registered blacklisted vehicle plates with reasons and FIR case references.
    """
    return db.query(Blacklist).order_by(Blacklist.created_at.desc()).offset(offset).limit(limit).all()

@router.post("", response_model=BlacklistResponse, status_code=status.HTTP_201_CREATED)
def add_to_blacklist(
    entry: BlacklistCreate,
    db: Session = Depends(get_db),
    authorized: bool = Depends(verify_api_key)
):
    """
    Registers a new vehicle plate to the hotlist/blacklist.
    """
    existing = db.query(Blacklist).filter(Blacklist.plate_number == entry.plate_number).first()
    if existing:
        existing.reason = entry.reason
        existing.reference_number = entry.reference_number
        existing.status = "ACTIVE"
        db.commit()
        db.refresh(existing)
        return existing

    new_bl = Blacklist(
        plate_number=entry.plate_number,
        reason=entry.reason,
        reference_number=entry.reference_number,
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_bl)

    audit = AuditLog(
        action_type="BLACKLIST_INSERT",
        entity_id=entry.plate_number,
        actor="POLICE_ADMIN",
        details=f"Plate {entry.plate_number} added to blacklist (Ref: {entry.reference_number})"
    )
    db.add(audit)

    db.commit()
    db.refresh(new_bl)
    return new_bl
