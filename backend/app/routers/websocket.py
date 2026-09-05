from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.websocket_manager import ws_manager

router = APIRouter(tags=["Real-Time WebSockets"])

@router.websocket("/ws/traffic")
async def websocket_traffic_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint broadcasting real-time ANPR events and alerts to connected dashboards.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep socket alive and receive client heartbeats/messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)
