from typing import List, Dict, Optional
from pydantic import BaseModel

class WeatherData(BaseModel):
    temperature_c: float
    apparent_temp_c: float
    humidity_pct: float
    wind_speed_kmh: float
    wind_gusts_kmh: float
    cloud_cover_pct: int
    direct_solar_irradiance: float
    weather_condition: str
    weather_code: int

class AirQualityData(BaseModel):
    us_aqi: int
    european_aqi: int
    aqi_category: str
    pm2_5: float
    pm10: float
    co: float
    no2: float
    so2: float
    ozone: float
    aerosol_optical_depth: float

class DroneFlightStatus(BaseModel):
    status: str  # "OPTIMAL_CLEARANCE", "CAUTION_ADVISORY", "GROUNDED"
    wind_clearance: str
    visibility_clearance: str
    solar_imaging_viability: str

class ForestRiskIndex(BaseModel):
    wildfire_risk_level: str  # "LOW", "MODERATE", "ELEVATED", "EXTREME"
    canopy_heat_stress: str
    recommended_irrigation: str

class TelemetryResponse(BaseModel):
    success: bool = True
    location_name: str
    country: str
    latitude: float
    longitude: float
    weather: WeatherData
    air_quality: AirQualityData
    flight_status: DroneFlightStatus
    forest_risk: ForestRiskIndex
    recommendations: List[str]
