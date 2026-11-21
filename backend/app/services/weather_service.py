from typing import List, Dict, Optional, Tuple
import requests
from backend.app.schemas.telemetry import (
    TelemetryResponse,
    WeatherData,
    AirQualityData,
    DroneFlightStatus,
    ForestRiskIndex
)

# WMO Weather Interpretation Codes
WMO_CODES = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog & Depositing Rime Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail"
}

def get_aqi_category(us_aqi: int) -> str:
    if us_aqi <= 50:
        return "Good"
    elif us_aqi <= 100:
        return "Moderate"
    elif us_aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif us_aqi <= 200:
        return "Unhealthy"
    elif us_aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

class ClimateTelemetryService:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "TreeSense_AI_Forestry_Platform/2.0"})

    def fetch_telemetry(
        self,
        city: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> TelemetryResponse:
        lat, lon, loc_name, country = self._resolve_location(city, latitude, longitude)

        weather_data = self._fetch_weather(lat, lon)
        air_data = self._fetch_air_quality(lat, lon)
        flight_status = self._evaluate_drone_flight(weather_data, air_data)
        forest_risk = self._evaluate_forest_risk(weather_data, air_data)
        recommendations = self._generate_recommendations(weather_data, air_data, flight_status, forest_risk)

        return TelemetryResponse(
            success=True,
            location_name=loc_name,
            country=country,
            latitude=round(lat, 4),
            longitude=round(lon, 4),
            weather=weather_data,
            air_quality=air_data,
            flight_status=flight_status,
            forest_risk=forest_risk,
            recommendations=recommendations
        )

    def _resolve_location(
        self,
        city: Optional[str],
        lat: Optional[float],
        lon: Optional[float]
    ) -> Tuple[float, float, str, str]:
        # If coordinates provided directly
        if lat is not None and lon is not None:
            # Reverse name fallback
            loc_label = city if city else f"Coordinate Plot ({lat:.2f}°N, {lon:.2f}°E)"
            return lat, lon, loc_label, "Field Jurisdiction"

        # Search city or forest name via Open-Meteo High-Speed Geocoding API (0 rate limits)
        target_query = city.strip() if city and city.strip() else "Bhopal"
        try:
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={target_query}&count=1&language=en&format=json"
            resp = self.session.get(url, timeout=4).json()
            if "results" in resp and resp["results"]:
                res = resp["results"][0]
                return (
                    float(res["latitude"]),
                    float(res["longitude"]),
                    res.get("name", target_query),
                    res.get("country", "")
                )
        except Exception:
            pass

        # Fallback to central forest research coordinates (Bhopal/Forest Survey of India zone)
        return 23.2547, 77.4029, target_query, "Central Zone"

    def _fetch_weather(self, lat: float, lon: float) -> WeatherData:
        try:
            url = (
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,"
                f"weather_code,cloud_cover,wind_speed_10m,wind_gusts_10m,direct_normal_irradiance"
            )
            resp = self.session.get(url, timeout=5).json()
            curr = resp.get("current", {})
            code = int(curr.get("weather_code", 0))
            return WeatherData(
                temperature_c=round(curr.get("temperature_2m", 24.0), 1),
                apparent_temp_c=round(curr.get("apparent_temperature", 24.5), 1),
                humidity_pct=round(curr.get("relative_humidity_2m", 55.0), 1),
                wind_speed_kmh=round(curr.get("wind_speed_10m", 8.0), 1),
                wind_gusts_kmh=round(curr.get("wind_gusts_10m", 12.0), 1),
                cloud_cover_pct=int(curr.get("cloud_cover", 15)),
                direct_solar_irradiance=round(curr.get("direct_normal_irradiance", 0.0), 1),
                weather_condition=WMO_CODES.get(code, "Clear Sky"),
                weather_code=code
            )
        except Exception:
            return WeatherData(
                temperature_c=25.0,
                apparent_temp_c=25.5,
                humidity_pct=50.0,
                wind_speed_kmh=10.0,
                wind_gusts_kmh=15.0,
                cloud_cover_pct=20,
                direct_solar_irradiance=450.0,
                weather_condition="Clear Sky",
                weather_code=0
            )

    def _fetch_air_quality(self, lat: float, lon: float) -> AirQualityData:
        try:
            url = (
                f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}"
                f"&current=us_aqi,european_aqi,pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,aerosol_optical_depth"
            )
            resp = self.session.get(url, timeout=5).json()
            curr = resp.get("current", {})
            us_aqi = int(curr.get("us_aqi", 65))
            return AirQualityData(
                us_aqi=us_aqi,
                european_aqi=int(curr.get("european_aqi", 25)),
                aqi_category=get_aqi_category(us_aqi),
                pm2_5=round(curr.get("pm2_5", 18.0), 1),
                pm10=round(curr.get("pm10", 35.0), 1),
                co=round(curr.get("carbon_monoxide", 350.0), 1),
                no2=round(curr.get("nitrogen_dioxide", 14.0), 1),
                so2=round(curr.get("sulphur_dioxide", 5.0), 1),
                ozone=round(curr.get("ozone", 30.0), 1),
                aerosol_optical_depth=round(curr.get("aerosol_optical_depth", 0.25), 2)
            )
        except Exception:
            return AirQualityData(
                us_aqi=55,
                european_aqi=20,
                aqi_category="Moderate",
                pm2_5=15.0,
                pm10=30.0,
                co=300.0,
                no2=12.0,
                so2=4.0,
                ozone=28.0,
                aerosol_optical_depth=0.20
            )

    def _evaluate_drone_flight(self, weather: WeatherData, air: AirQualityData) -> DroneFlightStatus:
        # Evaluate precipitation & violent thunderstorms
        if weather.weather_code >= 51 or weather.wind_gusts_kmh > 35.0:
            status = "GROUNDED"
            wind_eval = f"Exceeds Limit ({weather.wind_gusts_kmh} km/h gusts)"
        elif weather.wind_speed_kmh > 20.0 or weather.cloud_cover_pct > 65:
            status = "CAUTION_ADVISORY"
            wind_eval = f"Moderate Turbulence ({weather.wind_speed_kmh} km/h)"
        else:
            status = "OPTIMAL_CLEARANCE"
            wind_eval = f"Safe Low Wind ({weather.wind_speed_kmh} km/h)"

        # Atmospheric visibility
        if air.aerosol_optical_depth > 0.6 or weather.cloud_cover_pct > 80:
            vis_eval = "Sub-optimal (Atmospheric Haze / Clouds)"
        else:
            vis_eval = "High Transparency (Optimal Nadir Vision)"

        # Solar viability for VARI/GLI
        if weather.direct_solar_irradiance > 250.0 and weather.cloud_cover_pct < 40:
            solar_eval = "Prime Lighting for Calibrated VARI/GLI"
        else:
            solar_eval = "Diffuse Light / Shadow Compensation Recommended"

        return DroneFlightStatus(
            status=status,
            wind_clearance=wind_eval,
            visibility_clearance=vis_eval,
            solar_imaging_viability=solar_eval
        )

    def _evaluate_forest_risk(self, weather: WeatherData, air: AirQualityData) -> ForestRiskIndex:
        # Wildfire Danger index based on heat, low humidity, and wind
        if weather.temperature_c > 38.0 and weather.humidity_pct < 25.0 and weather.wind_speed_kmh > 20.0:
            fire_risk = "EXTREME"
            heat_stress = "Severe Chlorophyll Degradation Danger"
            irrigation = "Emergency Hydration Protocol"
        elif weather.temperature_c > 33.0 and weather.humidity_pct < 35.0:
            fire_risk = "ELEVATED"
            heat_stress = "Moderate Stomatal Closure & Thermal Strain"
            irrigation = "Recommended Deep Soil Rehydration"
        elif weather.temperature_c > 28.0:
            fire_risk = "MODERATE"
            heat_stress = "Normal Summer Canopy Evapotranspiration"
            irrigation = "Standard Cyclical Irrigation"
        else:
            fire_risk = "LOW"
            heat_stress = "Optimal Ecological Photosynthetic Regime"
            irrigation = "Baseline Rainfall Sustained"

        return ForestRiskIndex(
            wildfire_risk_level=fire_risk,
            canopy_heat_stress=heat_stress,
            recommended_irrigation=irrigation
        )

    def _generate_recommendations(
        self,
        weather: WeatherData,
        air: AirQualityData,
        flight: DroneFlightStatus,
        risk: ForestRiskIndex
    ) -> List[str]:
        recs = []
        if flight.status == "OPTIMAL_CLEARANCE":
            recs.append("🚁 Drone Flight Clearance: Optimal atmospheric conditions for high-speed photogrammetry and LiDAR orthomosaics.")
        elif flight.status == "CAUTION_ADVISORY":
            recs.append("⚠️ Drone Caution: Reduce flight altitude and enable gimbal stabilization due to moderate wind shear.")
        else:
            recs.append("⛔ Grounded Alert: High wind gusts or precipitation detected. Do not deploy autonomous UAV missions.")

        if risk.wildfire_risk_level in ["ELEVATED", "EXTREME"]:
            recs.append("🔥 Wildfire Vulnerability: Atmospheric moisture deficit detected. Activate thermal UAV perimeter patrols.")

        if air.us_aqi > 150:
            recs.append("🏭 Particulate Deposition Alert: Elevated PM2.5/PM10 haze can attenuate spectral reflectance; calibrate RGB white balance.")
        else:
            recs.append("🌿 Clean Canopy Atmosphere: Minimal aerosol scattering; RGB indices (VARI, GLI, ExG) will achieve peak radiometric precision.")

        return recs

climate_telemetry_service = ClimateTelemetryService()
