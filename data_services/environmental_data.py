"""
Environmental Data Services
Consolidated module for weather and air quality data fetching
"""

import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim
import requests

# ==============================
# WEATHER DATA FUNCTIONS
# ==============================

def get_coordinates(city_name):
    """Convert city name to latitude & longitude coordinates"""
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(city_name)
    if location:
        return location.latitude, location.longitude
    else:
        raise ValueError("City not found. Please try another name.")

def fetch_weather(city_name):
    """Fetch weather data for a given city"""
    # Get lat/lon from city
    latitude, longitude = get_coordinates(city_name)
    print(f"\n📍 City: {city_name} | Lat: {latitude}, Lon: {longitude}")

    # Setup Open-Meteo client
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # API request
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ["temperature_2m", "weather_code", "wind_speed_10m", "wind_direction_180m"],
    }
    responses = openmeteo.weather_api(url, params=params)

    # Process response
    for response in responses:
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "weather_code": hourly.Variables(1).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(2).ValuesAsNumpy(),
            "wind_direction_180m": hourly.Variables(3).ValuesAsNumpy(),
        }

        df = pd.DataFrame(hourly_data)
        print("\n✅ Hourly Weather Data\n", df.head(10))  # show first 10 rows
        return df  # return DataFrame for further use

# ==============================
# AIR QUALITY DATA FUNCTIONS
# ==============================

# OpenWeather API key
API_KEY = "938c0134212aebf7ef23844e386dc26d"

# Friendly labels for pollutants
pollutant_labels = {
    "co": "Carbon Monoxide (CO)",
    "no": "Nitric Oxide (NO)",
    "no2": "Nitrogen Dioxide (NO₂)",
    "o3": "Ozone (O₃)",
    "so2": "Sulphur Dioxide (SO₂)",
    "pm2_5": "Fine Particles (PM2.5)",
    "pm10": "Coarse Particles (PM10)",
    "nh3": "Ammonia (NH₃)"
}

# AQI meaning dictionary
aqi_meaning = {
    1: "Good ✅",
    2: "Fair 🙂",
    3: "Moderate 😐",
    4: "Poor 😷",
    5: "Very Poor ☠️"
}

def fetch_air_quality(city):
    """Fetch air quality data for a given city"""
    # Get coordinates
    geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}"
    geo_response = requests.get(geo_url).json()
    if not geo_response:
        return None, None, "City not found"

    lat, lon = geo_response[0]["lat"], geo_response[0]["lon"]

    # Get air quality
    air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    air_response = requests.get(air_url).json()
    if "list" not in air_response or not air_response["list"]:
        return None, None, "No air quality data available"

    aqi = air_response["list"][0]["main"]["aqi"]
    components = air_response["list"][0]["components"]

    # Rename pollutants
    df = pd.DataFrame([components]).rename(columns=pollutant_labels)

    return df, aqi, None

# ==============================
# UTILITY FUNCTIONS
# ==============================

def get_weather_description(weather_code):
    """Convert weather code to human-readable description"""
    weather_descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        95: "Thunderstorm",
    }
    return weather_descriptions.get(weather_code, "Unknown weather condition")

def get_aqi_color(aqi):
    """Get color for AQI levels"""
    if aqi <= 50:
        return "#4CAF50"  # Green
    elif aqi <= 100:
        return "#FFEB3B"  # Yellow
    elif aqi <= 150:
        return "#FF9800"  # Orange
    elif aqi <= 200:
        return "#F44336"  # Red
    elif aqi <= 300:
        return "#9C27B0"  # Purple
    else:
        return "#795548"  # Brown

def get_aqi_description(aqi):
    """Get descriptive text for AQI levels"""
    if aqi <= 50:
        return "Air quality is considered satisfactory, and air pollution poses little or no risk."
    elif aqi <= 100:
        return "Air quality is acceptable; however, there may be a moderate health concern for a very small number of people."
    elif aqi <= 150:
        return "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
    elif aqi <= 200:
        return "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects."
    elif aqi <= 300:
        return "Health alert: everyone may experience more serious health effects."
    else:
        return "Health warnings of emergency conditions. The entire population is more likely to be affected."
