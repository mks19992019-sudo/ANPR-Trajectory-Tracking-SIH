from fastapi import APIRouter
from backend.app.schemas.schemas import PredictionPlaceholderResponse

router = APIRouter(prefix="/ml", tags=["ML Traffic Forecast (Model Integration Point)"])

@router.get("/prediction", response_model=PredictionPlaceholderResponse)
def get_prediction_placeholder():
    """
    Architectural interface endpoint for future XGBoost traffic flow prediction model.
    No model is pre-trained or fabricated; this endpoint is ready to load traffic_model.json
    once trained and deployed.
    """
    return PredictionPlaceholderResponse(
        status="READY_FOR_MODEL",
        message="XGBoost model pipeline interface ready. Please train and supply traffic_model.json to activate live inference.",
        model_version=None,
        corridors=[]
    )
