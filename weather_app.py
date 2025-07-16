# -*- coding: utf-8 -*-
"""
WeatherNow by Arideep 🌦️
=========================

An interactive Streamlit app showing current weather, weekly temperature & rainfall forecast,
and mapping 40,000+ cities worldwide—all timezone-aware.

- Weather powered by: http://open-meteo.com
- Global cities from: https://simplemaps.com/data/world-cities

Stay curious & weather-wise! ☁️
"""

import streamlit as st
import pandas as pd
import requests
import json
from plotly.subplots import make_subplots
import plotly.graph_objs as go
from datetime import datetime
from datetime import timezone as tmz
import pytz
from tzwhere import tzwhere
import folium
from streamlit_folium import folium_static

# 🌍 Title & Location Selection
st.title("🌤️ Arideep's WeatherNow")
st.subheader("📍 Choose your city")

data = pd.read_csv("worldcities.csv")

country = st.selectbox('🌎 Country', options=sorted(set(data['country'])))
city = st.selectbox('🏙️ City', options=sorted(data[data['country'] == country]['city_ascii']))

lat = float(data[(data['country'] == country) & (data['city_ascii'] == city)]["lat"])
lng = float(data[(data['country'] == country) & (data['city_ascii'] == city)]["lng"])

# 🔥 Current Weather
st.subheader("🌡️ Live Weather Update")

res = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&current_weather=true')
current = json.loads(res._content)["current_weather"]
temp, speed, direction = current["temperature"], current["windspeed"], current["winddirection"]

# 🧭 Wind Direction Labeling
ddeg = 11.25
dirs = ["N", "N/NE", "NE", "E/NE", "E", "E/SE", "SE", "S/SE", "S", "S/SW", "SW", "W/SW", "W", "W/NW", "NW", "N/NW"]
common_dir = dirs[int((direction + ddeg / 2) // ddeg) % 16]

st.info(f"🌡️ Temperature: **{temp}°C**\n💨 Wind: **{speed} m/s** from **{common_dir}**")

# 📅 Weekly Forecast
st.subheader("📆 Weekly Forecast & Map")
st.write("Temperature 🌡️ and Rain 🌧️ forecast + Interactive Map")

with st.spinner("Fetching forecast data..."):
    hourly_res = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lng}&hourly=temperature_2m,precipitation')
    hourly = json.loads(hourly_res._content)["hourly"]
    df = pd.DataFrame(hourly).rename(columns={"time":"Week ahead", "temperature_2m":"Temperature °C", "precipitation":"Precipitation mm"})

    # 🕒 Timezone handling
    tz = tzwhere.tzwhere(forceTZ=True)
    timezone_str = tz.tzNameAt(lat, lng, forceTZ=True)
    timezone_loc = pytz.timezone(timezone_str)
    offset = timezone_loc.utcoffset(datetime.now())

    week_time = pd.to_datetime(df['Week ahead'], format="%Y-%m-%dT%H:%M")
    
    # 📊 Plotly Dual-Axis Chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=week_time+offset, y=df['Temperature °C'], name="Temperature °C"), secondary_y=False)
    fig.add_trace(go.Bar(x=week_time+offset, y=df['Precipitation mm'], name="Precipitation mm"), secondary_y=True)

    now = datetime.now(tmz.utc) + offset
    fig.add_vline(x=now, line_color="red", opacity=0.4)
    fig.add_annotation(x=now, y=max(df['Temperature °C'])+5, text=now.strftime("%d %b %Y %H:%M"), showarrow=False)

    fig.update_yaxes(title_text="🌡️ Temp (°C)", secondary_y=False)
    fig.update_yaxes(title_text="💧 Rain (mm)", secondary_y=True)
    fig.update_layout(legend=dict(orientation="h", y=1.02, x=0.7))

    # 🗺️ Map
    m = folium.Map(location=[lat, lng], zoom_start=7)
    folium.Marker([lat, lng], popup=f"{city}, {country}", tooltip=f"{city}, {country}").add_to(m)

    # 🔄 Responsive map
    st.markdown('<style>[title~="st.iframe"] { width: 100% }</style>', unsafe_allow_html=True)
    
    st.plotly_chart(fig, use_container_width=True)
    folium_static(m, height=370)

# ℹ️ Footer
st.write("🔗 Weather data: [open-meteo.com](http://open-meteo.com)")
st.write("📍 Cities database: [simplemaps.com](https://simplemaps.com/data/world-cities)")
st.write("👨‍💻 Modified with ❤️ by [Arideep](https://github.com/ArideepCodes)")
