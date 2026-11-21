from fastapi import APIRouter
from backend.app.api.v1.endpoints import detection, canopy, change, pathfinding, telemetry

api_router = APIRouter()

api_router.include_router(detection.router, prefix="/detection", tags=["AI Detection & Enumeration"])
api_router.include_router(canopy.router, prefix="/canopy", tags=["Spectral Vegetation Analytics"])
api_router.include_router(change.router, prefix="/change", tags=["Change Detection & Deforestation Alert"])
api_router.include_router(pathfinding.router, prefix="/pathfinding", tags=["Terrain A* Pathfinding"])
api_router.include_router(telemetry.router, prefix="/telemetry", tags=["Climate & Air Quality Telemetry"])
