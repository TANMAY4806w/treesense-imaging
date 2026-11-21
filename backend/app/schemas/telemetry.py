from typing import List, Dict, Optional
from pydantic import BaseModel

class WeatherData(BaseModel):
    temperature_c: float
    humidity_pct: float
    wind_speed_kmh: float
    weather_condition: str

class AirQualityData(BaseModel):
    aqi_index: int
    aqi_category: str
    pollutants: Dict[str, float]

class TelemetryResponse(BaseModel):
    success: bool = True
    city: str
    latitude: float
    longitude: float
    weather: Optional[WeatherData] = None
    air_quality: Optional[AirQualityData] = None
    recommendations: List[str]
