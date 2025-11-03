"""
UI Components for Historical Data Page
Contains all display and rendering functions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, timedelta
from .environmental_data import get_weather_description, get_aqi_color, get_aqi_description

def display_weather_data(weather_data):
    """Display weather data in a visually appealing format"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">🌤️ Current Weather Conditions</h3>', unsafe_allow_html=True)
    
    # Main weather metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌡️ Temperature", f"{weather_data['temperature']}°C", f"{weather_data['feels_like']}°C feels like")
    
    with col2:
        st.metric("💧 Humidity", f"{weather_data['humidity']}%", "")
    
    with col3:
        st.metric("💨 Wind Speed", f"{weather_data['wind_speed']} m/s", "")
    
    with col4:
        st.metric("👓 Visibility", f"{weather_data['visibility']} km", "")
    
    # Weather description
    st.markdown(f"""
    <div style="background: rgba(46, 139, 87, 0.1); padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem;">
        <h4 style="margin-top: 0; color: var(--text-light);">📝 Weather Description</h4>
        <p style="font-size: 1.2rem; color: var(--text-secondary);">{weather_data['description'].title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_air_quality_data(air_quality_data):
    """Display air quality data with AQI visualization"""
    st.markdown('<div class="aqi-card">', unsafe_allow_html=True)
    st.markdown('<h3 class="aqi-title">🌍 Air Quality Index</h3>', unsafe_allow_html=True)
    
    # AQI level and label
    aqi = air_quality_data['aqi']
    aqi_label = get_aqi_description(aqi)
    aqi_color = get_aqi_color(aqi)
    
    st.markdown(f'<div class="aqi-level">{aqi}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="aqi-label" style="color: {aqi_color};">{aqi_label}</div>', unsafe_allow_html=True)
    
    # AQI description
    st.markdown(f'<p class="aqi-description">{get_aqi_description(aqi)}</p>', unsafe_allow_html=True)
    
    # Pollutant levels
    st.markdown('<h4 style="color: var(--text-light); margin: 2rem 0 1rem 0;">🔬 Pollutant Levels</h4>', unsafe_allow_html=True)
    
    pollutants = [
        ("PM2.5", air_quality_data['pm2_5'], "μg/m³"),
        ("PM10", air_quality_data['pm10'], "μg/m³"),
        ("O₃", air_quality_data['o3'], "μg/m³"),
        ("NO₂", air_quality_data['no2'], "μg/m³"),
        ("SO₂", air_quality_data['so2'], "μg/m³"),
        ("CO", air_quality_data['co'], "mg/m³")
    ]
    
    cols = st.columns(3)
    for i, (name, value, unit) in enumerate(pollutants):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background: var(--card-bg); padding: 1rem; border-radius: 12px; margin-bottom: 1rem; box-shadow: var(--shadow); text-align: center;">
                <h4 style="margin: 0 0 0.5rem 0; color: var(--text-light);">{name}</h4>
                <div style="font-size: 1.5rem; font-weight: bold; color: var(--text-secondary);">{value} {unit}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_historical_analysis(city):
    """Display historical data analysis with charts and graphs"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">📊 Historical Environmental Analysis</h3>', unsafe_allow_html=True)
    
    # Generate sample historical data for visualization
    from .data_analysis import generate_sample_historical_data
    historical_data = generate_sample_historical_data()
    
    # Create tabs for different historical analysis
    hist_tab1, hist_tab2, hist_tab3 = st.tabs(["🌡️ Temperature Trends", "💨 Air Quality History", "📈 Environmental Correlations"])
    
    with hist_tab1:
        display_temperature_trends(historical_data)
    
    with hist_tab2:
        display_air_quality_history(historical_data)
    
    with hist_tab3:
        display_environmental_correlations(historical_data)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_temperature_trends(historical_data):
    """Display temperature trends with interactive charts"""
    st.markdown("### 🌡️ Temperature Trends Analysis")
    
    # Line chart of temperature over time
    fig_temp = px.line(
        historical_data, 
        x='Date', 
        y='Temperature',
        title='Temperature Trends Over Time',
        labels={'Temperature': 'Temperature (°C)', 'Date': 'Date'},
        line_shape='spline'
    )
    fig_temp.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    
    # Monthly average temperature
    historical_data['Month'] = historical_data['Date'].dt.month_name()
    monthly_avg = historical_data.groupby('Month')['Temperature'].mean().reset_index()
    
    fig_monthly = px.bar(
        monthly_avg,
        x='Month',
        y='Temperature',
        title='Average Monthly Temperature',
        labels={'Temperature': 'Average Temperature (°C)'},
        color='Temperature',
        color_continuous_scale='temps'
    )
    fig_monthly.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

def display_air_quality_history(historical_data):
    """Display air quality history with charts"""
    st.markdown("### 🌬️ Air Quality History")
    
    # AQI over time
    fig_aqi = px.line(
        historical_data,
        x='Date',
        y='AQI',
        title='Air Quality Index (AQI) Over Time',
        labels={'AQI': 'Air Quality Index', 'Date': 'Date'},
        line_shape='spline'
    )
    fig_aqi.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_aqi, use_container_width=True)
    
    # AQI categories
    def categorize_aqi(aqi):
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            return "Unhealthy"
        else:
            return "Very Unhealthy"
    
    historical_data['AQI_Category'] = historical_data['AQI'].apply(categorize_aqi)
    category_counts = historical_data['AQI_Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']
    
    fig_aqi_pie = px.pie(
        category_counts,
        values='Count',
        names='Category',
        title='Distribution of Air Quality Categories',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_aqi_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_aqi_pie, use_container_width=True)

def display_environmental_correlations(historical_data):
    """Display correlations between environmental factors"""
    st.markdown("### 📈 Environmental Factor Correlations")
    
    # Correlation heatmap
    correlation_cols = ['Temperature', 'Humidity', 'AQI', 'Rainfall', 'Wind_Speed']
    correlation_matrix = historical_data[correlation_cols].corr()
    
    fig_corr = px.imshow(
        correlation_matrix,
        title='Correlation Between Environmental Factors',
        color_continuous_scale='RdBu',
        aspect="auto"
    )
    fig_corr.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Scatter plot: Temperature vs AQI
    fig_scatter = px.scatter(
        historical_data,
        x='Temperature',
        y='AQI',
        title='Temperature vs Air Quality Index',
        trendline='ols',
        labels={'Temperature': 'Temperature (°C)', 'AQI': 'Air Quality Index'}
    )
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Show correlation statistics
    st.markdown("#### Correlation Insights")
    temp_aqi_corr = historical_data['Temperature'].corr(historical_data['AQI'])
    st.info(f"**Temperature and AQI Correlation:** {temp_aqi_corr:.2f}")
    st.write("A positive correlation indicates that as temperature increases, air quality tends to worsen.")

def display_recommendations(weather_data, air_quality_data):
    """Display environmental recommendations based on current conditions"""
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="chart-title">💡 Environmental Recommendations</h3>', unsafe_allow_html=True)
    
    # Generate recommendations based on data
    from .data_analysis import generate_recommendations
    recommendations = generate_recommendations(weather_data, air_quality_data)
    
    for rec in recommendations:
        st.markdown(f"""
        <div class="suggestion-card {'suggestion-sufficient' if 'good' in rec.lower() or 'sufficient' in rec.lower() else 'suggestion-needed'}">
            {rec}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
