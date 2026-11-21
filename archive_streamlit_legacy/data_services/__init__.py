"""
Data Services Package
Contains environmental data fetching, UI components, and analysis functions for TreeSense Imaging
"""

from .environmental_data import (
    fetch_weather,
    fetch_air_quality,
    aqi_meaning,
    get_weather_description,
    get_aqi_color,
    get_aqi_description
)

from .ui_components import (
    display_weather_data,
    display_air_quality_data,
    display_historical_analysis,
    display_recommendations,
    display_temperature_trends,
    display_air_quality_history,
    display_environmental_correlations
)

from .data_analysis import (
    generate_sample_historical_data,
    generate_recommendations,
    process_weather_data,
    process_air_quality_data
)

__all__ = [
    # Environmental data functions
    'fetch_weather',
    'fetch_air_quality', 
    'aqi_meaning',
    'get_weather_description',
    'get_aqi_color',
    'get_aqi_description',
    
    # UI components
    'display_weather_data',
    'display_air_quality_data',
    'display_historical_analysis',
    'display_recommendations',
    'display_temperature_trends',
    'display_air_quality_history',
    'display_environmental_correlations',
    
    # Data analysis functions
    'generate_sample_historical_data',
    'generate_recommendations',
    'process_weather_data',
    'process_air_quality_data'
]
