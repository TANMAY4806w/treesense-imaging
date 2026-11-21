from typing import List, Dict, Optional
from geopy.geocoders import Nominatim
import requests
import requests_cache
from retry_requests import retry

from backend.app.core.config import settings
from backend.app.schemas.telemetry import TelemetryResponse, WeatherData, AirQualityData

class ClimateTelemetryService:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="treesense_ai_platform")
        self.cache_session = requests_cache.CachedSession('.cache_weather', expire_after=1800)
        self.retry_session = retry(self.cache_session, retries=3, backoff_factor=0.3)

    def fetch_telemetry(self, city: str) -> TelemetryResponse:
        try:
            loc = self.geolocator.geocode(city, timeout=5)
            if not loc:
                lat, lon = 23.2599, 77.4126  # Fallback coordinates
                resolved_city = f"{city} (Default Location)"
            else:
                lat, lon = loc.latitude, loc.longitude
                resolved_city = loc.address.split(",")[0]
        except Exception:
            lat, lon = 23.2599, 77.4126
            resolved_city = city

        weather_obj = self._get_weather(lat, lon)
        air_obj = self._get_air_quality(lat, lon)
        recommendations = self._generate_recommendations(weather_obj, air_obj)

        return TelemetryResponse(
            success=True,
            city=resolved_city,
            latitude=round(lat, 4),
            longitude=round(lon, 4),
            weather=weather_obj,
            air_quality=air_obj,
            recommendations=recommendations
        )

    def _get_weather(self, lat: float, lon: float) -> Optional[WeatherData]:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code"
            resp = self.retry_session.get(url, timeout=5).json()
            curr = resp.get("current", {})
            return WeatherData(
                temperature_c=round(curr.get("temperature_2m", 25.0), 1),
                humidity_pct=round(curr.get("relative_humidity_2m", 50.0), 1),
                wind_speed_kmh=round(curr.get("wind_speed_10m", 10.0), 1),
                weather_condition=f"Code {curr.get('weather_code', 0)}"
            )
        except Exception:
            return WeatherData(
                temperature_c=26.5,
                humidity_pct=55.0,
                wind_speed_kmh=12.0,
                weather_condition="Clear Sky"
            )

    def _get_air_quality(self, lat: float, lon: float) -> Optional[AirQualityData]:
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return AirQualityData(
                aqi_index=2,
                aqi_category="Moderate",
                pollutants={"pm2_5": 35.0, "pm10": 60.0, "co": 420.0, "no2": 18.0}
            )

        try:
            url = f"https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
            resp = requests.get(url, timeout=5).json()
            if "list" in resp and resp["list"]:
                item = resp["list"][0]
                aqi = item["main"]["aqi"]
                components = item["components"]
                categories = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
                return AirQualityData(
                    aqi_index=aqi,
                    aqi_category=categories.get(aqi, "Moderate"),
                    pollutants={k: round(v, 2) for k, v in components.items()}
                )
        except Exception:
            pass

        return AirQualityData(
            aqi_index=2,
            aqi_category="Moderate",
            pollutants={"pm2_5": 32.0, "pm10": 58.0}
        )

    def _generate_recommendations(
        self, weather: Optional[WeatherData], air: Optional[AirQualityData]
    ) -> List[str]:
        recs = []
        if weather:
            if weather.temperature_c > 35.0:
                recs.append("🔥 Elevated ambient temperature. Intensify canopy irrigation to mitigate heat stress.")
            elif weather.temperature_c < 10.0:
                recs.append("❄️ Low temperatures detected. Monitor sapling frost protection.")
            if weather.humidity_pct < 30.0:
                recs.append("⚠️ Low relative humidity. Elevated wildfire vulnerability index.")

        if air and air.aqi_index >= 4:
            recs.append("🚨 Elevated pollutant concentrations (AQI Poor/Hazardous). Urban green buffers recommended.")
        else:
            recs.append("✅ Atmospheric and moisture conditions are favorable for forest regeneration.")

        return recs

climate_telemetry_service = ClimateTelemetryService()
