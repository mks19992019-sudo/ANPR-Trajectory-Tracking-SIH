from fastapi import APIRouter
from backend.app.schemas.schemas import PredictionPlaceholderResponse

router = APIRouter(prefix="/ml", tags=["ML Traffic Forecast (Placeholder)"])

@router.get("/prediction", response_model=PredictionPlaceholderResponse)
def get_prediction_placeholder():
    """
    Clean architectural placeholder interface for future XGBoost traffic volume prediction.
    As instructed, no model is pre-trained or fabricated; this endpoint is ready to load
    traffic_model.json once the user trains and provides the model.
    """
    return PredictionPlaceholderResponse(
        status="READY_FOR_MODEL",
        message="XGBoost model pipeline interface ready. Please train and supply traffic_model.json to activate live inference.",
        model_version=None,
        corridors=[]
    )
