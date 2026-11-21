from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from backend.app.schemas.telemetry import TelemetryResponse
from backend.app.services.weather_service import climate_telemetry_service

router = APIRouter()

@router.get("/telemetry", response_model=TelemetryResponse, summary="Retrieve climate and air quality telemetry for a region or GPS coordinate")
async def get_climate_telemetry(
    city: Optional[str] = Query(None, description="City name or forest jurisdiction"),
    latitude: Optional[float] = Query(None, description="GPS Latitude"),
    longitude: Optional[float] = Query(None, description="GPS Longitude")
):
    try:
        response = climate_telemetry_service.fetch_telemetry(
            city=city,
            latitude=latitude,
            longitude=longitude
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Telemetry retrieval failure: {str(e)}")
