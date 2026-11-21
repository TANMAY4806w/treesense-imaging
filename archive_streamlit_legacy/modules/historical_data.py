

"""
historical_data.py
Improved Streamlit Historical Data page with modern dark UI
"""

import streamlit as st
from data_services import fetch_weather, fetch_air_quality
from data_services.ui_components import (
    display_weather_data,
    display_air_quality_data,
    display_historical_analysis,
    display_recommendations,
)
from data_services.data_analysis import process_weather_data, process_air_quality_data


def _aqi_category(aqi: int):
    """
    Return (category_name, short_description, hex_color) for a numeric AQI.
    Standard categories (US EPA-style).
    """
    try:
        aqi = int(aqi)
    except Exception:
        return ("Unknown", "AQI unavailable", "#64748b")

    if aqi <= 50:
        return ("Good", "Air quality is satisfactory and poses little or no risk.", "#10b981")
    if aqi <= 100:
        return ("Moderate", "Air quality is acceptable. Some pollutants may be a concern for sensitive people.", "#eab308")
    if aqi <= 150:
        return ("Unhealthy for Sensitive Groups", "Members of sensitive groups may experience health effects.", "#f97316")
    if aqi <= 200:
        return ("Unhealthy", "Everyone may begin to experience health effects; sensitive groups more so.", "#ef4444")
    if aqi <= 300:
        return ("Very Unhealthy", "Health alert: everyone may experience more serious health effects.", "#a855f7")
    return ("Hazardous", "Health warnings of emergency conditions. The entire population is more likely to be affected.", "#7c3aed")


def _render_aqi_summary(aqi):
    """Render an attractive AQI summary card as HTML."""
    category, desc, color = _aqi_category(aqi)
    aqi_display = aqi if aqi is not None else "N/A"

    html = f"""
    <div style="
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.8), rgba(30, 41, 59, 0.6));
        padding: 24px;
        border-radius: 14px;
        display: flex;
        gap: 24px;
        align-items: center;
        border: 2px solid {color}40;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    ">
        <div style="flex: 0 0 auto; text-align: center; min-width: 120px;">
            <div style="font-size: 48px; font-weight: 900; color: {color}; margin-bottom: 8px;">{aqi_display}</div>
            <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">AQI Score</div>
        </div>
        <div style="flex: 1 1 auto;">
            <div style="font-size: 20px; font-weight: 800; color: #f1f5f9; margin-bottom: 8px;">{category}</div>
            <div style="color: #cbd5e1; font-size: 14px; line-height: 1.5;">{desc}</div>
        </div>
        <div style="flex: 0 0 auto;">
            <div style="background: linear-gradient(135deg, {color}, {color}dd); color: #fff; padding: 10px 18px; border-radius: 50px; font-weight: 700; font-size: 13px; box-shadow: 0 4px 12px {color}40;">
                {category.split()[0]}
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def load_custom_css():
    """Load all custom CSS for the page"""
    st.markdown("""
    <style>
        /* Root colors */
        :root {
            --primary-green: #10b981;
            --primary-green-light: #34d399;
            --primary-green-dark: #059669;
            --card-bg: #1e293b;
            --card-bg-light: #334155;
            --text-light: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-tertiary: #94a3b8;
            --border-color: #475569;
            --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 12px 32px rgba(0, 0, 0, 0.5);
        }

        /* Page background */
        .main {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f2f4f 100%);
            color: var(--text-light);
        }

        body {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f2f4f 100%);
        }

        /* Dashboard header */
        .dashboard-header {
            background: linear-gradient(135deg, var(--primary-green) 0%, var(--primary-green-light) 100%);
            padding: 36px;
            border-radius: 16px;
            margin-bottom: 32px;
            box-shadow: var(--shadow-lg);
            text-align: center;
            animation: slideDown 0.6s ease-out;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .dashboard-title {
            font-size: 2.8rem;
            font-weight: 900;
            margin: 0;
            color: #fff;
            letter-spacing: -0.5px;
        }

        .dashboard-subtitle {
            font-size: 1rem;
            color: rgba(255, 255, 255, 0.95);
            margin-top: 12px;
            font-weight: 500;
        }

        /* Input section */
        .input-section {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 28px;
            border-radius: 14px;
            box-shadow: var(--shadow-md);
            margin-bottom: 24px;
            border: 1px solid var(--border-color);
            animation: fadeIn 0.6s ease-out 0.2s both;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Cards */
        .card {
            background: linear-gradient(135deg, var(--card-bg) 0%, #0f172a 100%);
            padding: 24px;
            border-radius: 14px;
            box-shadow: var(--shadow-md);
            margin-bottom: 20px;
            border: 1px solid rgba(71, 85, 105, 0.3);
            transition: all 0.3s ease;
        }

        .card:hover {
            border-color: var(--border-color);
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
        }

        /* Welcome cards grid */
        .welcome-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 20px;
        }

        .welcome-item {
            padding: 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.03));
            border: 1px solid rgba(16, 185, 129, 0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .welcome-item:hover {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.12), rgba(16, 185, 129, 0.05));
            border-color: rgba(16, 185, 129, 0.4);
            transform: translateY(-4px);
        }

        .welcome-item h4 {
            margin: 0 0 8px 0;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-light);
        }

        .welcome-item p {
            margin: 0;
            color: var(--text-tertiary);
            font-size: 0.95rem;
            line-height: 1.5;
        }

        /* Tabs styling */
        [data-baseweb="tab-list"] {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 12px 8px !important;
            border-bottom: 1px solid rgba(71, 85, 105, 0.2) !important;
        }

        [data-baseweb="tab"] {
            background: rgba(255, 255, 255, 0.02) !important;
            color: var(--text-tertiary) !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            margin: 0 8px !important;
            transition: all 0.3s ease;
            border: 1px solid transparent !important;
            font-weight: 600 !important;
        }

        [data-baseweb="tab"]:hover {
            background: rgba(16, 185, 129, 0.08) !important;
            color: var(--text-light) !important;
            transform: translateY(-2px);
        }

        [data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.08)) !important;
            color: var(--primary-green) !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.1) !important;
        }

        /* Input fields */
        .stTextInput > div > div > input {
            background-color: var(--card-bg-light) !important;
            color: var(--text-light) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 10px !important;
            padding: 12px 16px !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }

        .stTextInput > div > div > input:focus {
            border-color: var(--primary-green) !important;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1) !important;
        }

        .stTextInput > label {
            display: none !important;
        }

        /* Button */
        .stButton > button {
            background: linear-gradient(135deg, var(--primary-green), var(--primary-green-light)) !important;
            color: #fff !important;
            border-radius: 10px !important;
            padding: 12px 28px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3) !important;
            border: none !important;
        }

        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 12px 28px rgba(16, 185, 129, 0.4) !important;
        }

        .stButton > button:active {
            transform: translateY(-1px) !important;
        }

        /* City header */
        .city-header {
            padding: 16px 20px;
            border-radius: 12px;
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05));
            border: 1px solid rgba(16, 185, 129, 0.2);
            margin-bottom: 24px;
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-light);
            animation: fadeIn 0.4s ease-out;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 24px 0;
            color: var(--text-tertiary);
            margin-top: 32px;
            font-size: 0.95rem;
            border-top: 1px solid rgba(71, 85, 105, 0.2);
        }

        /* Data frame and metrics */
        .stDataFrame, [data-testid="stMetric"] {
            background: transparent !important;
            color: var(--text-light) !important;
            border-radius: 10px !important;
        }

        /* Spinner animation */
        .stSpinner > div {
            border-color: var(--primary-green) !important;
        }

        /* Alert styling */
        .stSuccess {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(16, 185, 129, 0.05)) !important;
            color: #86efac !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            border-radius: 10px !important;
        }

        .stError {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(239, 68, 68, 0.05)) !important;
            color: #fca5a5 !important;
            border: 1px solid rgba(239, 68, 68, 0.3) !important;
            border-radius: 10px !important;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .dashboard-title {
                font-size: 1.8rem;
            }
            .dashboard-header {
                padding: 24px;
            }
            .welcome-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    """, unsafe_allow_html=True)


def show_historical_data_page():
    """Main function for Historical Data page"""
    st.set_page_config(page_title="Environmental Intelligence", layout="wide")

    # Load custom CSS
    load_custom_css()

    # ======================== HEADER ========================
    st.markdown("""
        <div class="dashboard-header">
            <div style="display: flex; gap: 18px; align-items: center; justify-content: center;">
                <div style="font-size: 36px;">🌍</div>
                <div>
                    <div class="dashboard-title">Environmental Intelligence</div>
                    <div class="dashboard-subtitle">Real-time weather & air quality analytics</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ======================== INPUT SECTION ========================
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    
    city = st.text_input("🏙️ Enter city name:", value="Mumbai", help="Enter city name to analyze environmental data", label_visibility="collapsed")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze = st.button("🔍 Analyze", use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # ======================== DEFAULT WELCOME VIEW ========================
    if not analyze:
        st.markdown("""
            <div class="card">
                <h3 style="margin: 0 0 12px 0; color: #f1f5f9; font-size: 1.3rem;">Welcome to Environmental Intelligence</h3>
                <div style="color: #cbd5e1; font-size: 1rem; line-height: 1.6;">
                    Monitor real-time weather patterns, track air quality (AQI), and analyze historical environmental trends. Enter a city name above to get started.
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="welcome-grid">
                <div class="welcome-item">
                    <h4>🌤️ Weather Monitoring</h4>
                    <p>Real-time temperature, humidity, wind speed, and atmospheric pressure insights.</p>
                </div>
                <div class="welcome-item">
                    <h4>🌍 Air Quality Tracking</h4>
                    <p>Comprehensive AQI summary, pollutant breakdown, and health recommendations.</p>
                </div>
                <div class="welcome-item">
                    <h4>📊 Historical Analysis</h4>
                    <p>Trend analysis over time and seasonal comparison patterns.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown('<div class="footer">© 2024 TreeSense Imaging | Environmental Intelligence</div>', unsafe_allow_html=True)
        return

    # ======================== ANALYZE CITY (MAIN LOGIC) ========================
    with st.spinner("📡 Fetching environmental data..."):
        try:
            # Fetch data
            weather_df = fetch_weather(city)
            air_quality_df, aqi, error = fetch_air_quality(city)

            # Process data
            weather_data = process_weather_data(weather_df)
            air_quality_data = process_air_quality_data(air_quality_df, aqi)

            # Success check
            if (weather_data is not None) and (air_quality_data is not None) and (error is None):
                st.success(f"✅ Environmental data for {city} loaded successfully!")

                # City header
                st.markdown(f"""
                    <div class="city-header">
                        📍 {city} <span style="color: #94a3b8; font-weight: 500; font-size: 0.9rem;">  •  Real-time Overview</span>
                    </div>
                """, unsafe_allow_html=True)

                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "🌤️ Weather", 
                    "🌍 Air Quality", 
                    "📊 Analysis", 
                    "🌱 Recommendations"
                ])

                # Tab 1: Weather
                with tab1:
                    display_weather_data(weather_data)

                # Tab 2: Air Quality
                with tab2:
                    _render_aqi_summary(aqi)
                    st.markdown("---")
                    display_air_quality_data(air_quality_data)

                # Tab 3: Historical Analysis
                with tab3:
                    display_historical_analysis(city)

                # Tab 4: Recommendations
                with tab4:
                    display_recommendations(weather_data, air_quality_data)

            else:
                error_msg = error if error else "Failed to fetch or process environmental data. Check the city name and try again."
                st.error(f"❌ {error_msg}")

        except Exception as exc:
            st.error(f"❌ An unexpected error occurred: {str(exc)}")

    # ======================== FOOTER ========================
    st.markdown('<div class="footer">© 2024 TreeSense Imaging | Environmental Intelligence</div>', unsafe_allow_html=True)