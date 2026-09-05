from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.entities import Alert, Camera, AuditLog
from backend.app.schemas.schemas import AlertResponse, AlertUpdate

router = APIRouter(prefix="/alerts", tags=["Incident & Alerts Management"])

@router.get("", response_model=List[AlertResponse])
def list_alerts(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Lists active and historical alerts filterable by severity and status with pagination.
    """
    query = db.query(Alert)
    if severity and severity.upper() != "ALL":
        query = query.filter(Alert.severity == severity.upper())
    if status and status.upper() != "ALL":
        query = query.filter(Alert.status == status.upper())

    alerts = query.order_by(Alert.timestamp.desc()).offset(offset).limit(limit).all()

    # Enrich with camera names
    cam_map = {c.camera_id: c.camera_name for c in db.query(Camera).all()}
    response = []
    for a in alerts:
        res = AlertResponse.model_validate(a)
        res.camera_name = cam_map.get(a.camera_id, a.camera_id)
        response.append(res)

    return response

@router.patch("/{alert_id}/status", response_model=AlertResponse)
@router.patch("/{alert_id}", response_model=AlertResponse)
def update_alert_status(
    alert_id: str,
    update_data: AlertUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates status of an alert (OPEN -> INVESTIGATING -> RESOLVED) and writes an audit log.
    """
    alert = db.query(Alert).filter(Alert.alert_id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found.")

    valid_statuses = ["OPEN", "INVESTIGATING", "RESOLVED"]
    norm_status = update_data.status.upper()
    if norm_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status '{update_data.status}'. Must be one of {valid_statuses}")

    old_status = alert.status
    alert.status = norm_status

    # Audit log
    audit = AuditLog(
        action_type="ALERT_STATUS_UPDATE",
        entity_id=alert.alert_id,
        actor="DISPATCH_OPERATOR",
        details=f"Alert {alert.alert_id} status transitioned from {old_status} to {norm_status}"
    )
    db.add(audit)
    db.commit()
    db.refresh(alert)
    return alert
