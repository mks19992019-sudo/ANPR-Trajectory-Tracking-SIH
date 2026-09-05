from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models.entities import Blacklist
from backend.app.schemas.schemas import BlacklistResponse

router = APIRouter(prefix="/blacklist", tags=["Police Blacklist"])

@router.get("", response_model=List[BlacklistResponse])
def get_blacklist(db: Session = Depends(get_db)):
    """
    Returns registered blacklisted vehicle plates with reasons and FIR case references.
    """
    return db.query(Blacklist).order_by(Blacklist.created_at.desc()).all()
