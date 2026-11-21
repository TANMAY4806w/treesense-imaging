"""
Data Analysis Functions for Historical Data
Contains data generation, processing, and analysis functions
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_historical_data():
    """Generate sample historical data for demonstration"""
    # Generate date range for the past year
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic environmental data
    data = []
    for i, date in enumerate(date_range):
        # Seasonal patterns
        day_of_year = date.timetuple().tm_yday
        base_temp = 20 + 15 * np.sin(2 * np.pi * day_of_year / 365)
        base_aqi = 50 + 30 * np.sin(2 * np.pi * day_of_year / 365)
        
        # Add some random variation
        temperature = base_temp + np.random.normal(0, 5)
        humidity = 60 + 20 * np.sin(2 * np.pi * day_of_year / 365) + np.random.normal(0, 10)
        aqi = max(10, min(200, base_aqi + np.random.normal(0, 15)))
        rainfall = max(0, 5 * np.sin(2 * np.pi * day_of_year / 365) + np.random.exponential(2))
        
        data.append({
            'Date': date,
            'Temperature': round(temperature, 1),
            'Humidity': round(humidity, 1),
            'AQI': round(aqi, 1),
            'Rainfall': round(rainfall, 1),
            'Wind_Speed': round(3 + np.random.exponential(2), 1)
        })
    
    return pd.DataFrame(data)

def generate_recommendations(weather_data, air_quality_data):
    """Generate environmental recommendations based on current data"""
    recommendations = []
    
    # Temperature-based recommendations
    temp = weather_data['temperature']
    if temp < 10:
        recommendations.append("🧊 Cold temperatures detected. Consider energy-efficient heating solutions.")
    elif temp > 35:
        recommendations.append("🔥 High temperatures detected. Increase green cover to reduce urban heat island effect.")
    else:
        recommendations.append("✅ Temperature is within optimal range for most activities.")
    
    # Humidity-based recommendations
    humidity = weather_data['humidity']
    if humidity < 30:
        recommendations.append("💧 Low humidity levels. Consider humidification for comfort and health.")
    elif humidity > 70:
        recommendations.append("💦 High humidity levels. Ensure proper ventilation to prevent mold growth.")
    else:
        recommendations.append("✅ Humidity levels are comfortable and healthy.")
    
    # Air quality recommendations
    aqi = air_quality_data['aqi']
    if aqi <= 50:
        recommendations.append("✅ Air quality is good. Ideal conditions for outdoor activities.")
    elif aqi <= 100:
        recommendations.append("⚠️ Air quality is moderate. Sensitive individuals should consider limiting prolonged outdoor exertion.")
    elif aqi <= 150:
        recommendations.append("⚠️ Air quality is unhealthy for sensitive groups. Children and elderly should reduce outdoor activities.")
    else:
        recommendations.append("🚨 Air quality is hazardous. Avoid outdoor activities and use air purifiers indoors.")
    
    # Wind-based recommendations
    wind_speed = weather_data['wind_speed']
    if wind_speed > 10:
        recommendations.append("💨 Strong winds detected. Secure loose outdoor items and check for potential hazards.")
    else:
        recommendations.append("✅ Wind conditions are calm and favorable.")
    
    return recommendations

def process_weather_data(weather_df):
    """Process weather data from API response"""
    if weather_df is not None and not weather_df.empty:
        latest_weather = weather_df.iloc[0]
        weather_data = {
            'temperature': round(latest_weather['temperature_2m'], 1),
            'feels_like': round(latest_weather['temperature_2m'], 1),  # Simplified
            'humidity': 60,  # Default value, Open-Meteo doesn't provide humidity in free tier
            'wind_speed': round(latest_weather['wind_speed_10m'], 1),
            'visibility': 10,  # Default value
            'description': get_weather_description(latest_weather['weather_code'])
        }
        return weather_data
    return None

def process_air_quality_data(air_quality_df, aqi):
    """Process air quality data from API response"""
    if air_quality_df is not None and not air_quality_df.empty:
        components = air_quality_df.iloc[0].to_dict()
        # Create air quality data dictionary
        air_quality_data = {
            'aqi': aqi,
            'co': components.get('Carbon Monoxide (CO)', 0),
            'no2': components.get('Nitrogen Dioxide (NO₂)', 0),
            'o3': components.get('Ozone (O₃)', 0),
            'so2': components.get('Sulphur Dioxide (SO₂)', 0),
            'pm2_5': components.get('Fine Particles (PM2.5)', 0),
            'pm10': components.get('Coarse Particles (PM10)', 0)
        }
        return air_quality_data
    return None

def get_weather_description(weather_code):
    """Convert weather code to description"""
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
