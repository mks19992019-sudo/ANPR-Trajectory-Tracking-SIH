from fastapi import APIRouter
from backend.app.schemas.schemas import ModelUnavailableResponse

router = APIRouter(prefix="/ml", tags=["ML integration"])


@router.get("/prediction", response_model=ModelUnavailableResponse)
def prediction():
    """Returns model status. Transparently communicates that ML inference requires training."""
    return ModelUnavailableResponse(
        status="MODEL_UNAVAILABLE",
        message="XGBoost model is not loaded. Train traffic_model.json using offline data to activate live inference."
    )
