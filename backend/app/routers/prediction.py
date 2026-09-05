from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from backend.app.schemas.schemas import ModelUnavailableResponse
router=APIRouter(prefix="/ml",tags=["ML integration"])
@router.get("/prediction", response_model=ModelUnavailableResponse)
def prediction():
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content=ModelUnavailableResponse().model_dump())
