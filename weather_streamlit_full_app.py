
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Weather Contest Dashboard", layout="wide")
st.title("🌤️ SWM Weather Contest Dashboard")
st.caption("Based on ECMWF and GFS models | Period: 8:30 AM to 8:30 AM IST")

# Define contest locations
locations = {
    "Nungambakkam": (13.0632, 80.2495),
    "Meenambakkam": (12.9941, 80.1808),
    "Sriperumbudur": (13.0300, 79.9495),
    "Mahabalipuram": (12.6208, 80.1930),
    "Gummidipoondi": (13.4072, 80.1085),
    "Cholavaram": (13.2150, 80.1833),
    "Dharmapuri": (12.1211, 78.1580),
    "Ooty PTO": (11.4102, 76.6950),
    "Kodaikanal": (10.2381, 77.4892),
    "Pasighat": (28.0667, 95.3333)
}

start_time = datetime.now().replace(hour=8, minute=30, second=0, microsecond=0)
end_time = start_time + timedelta(days=1)
start_iso = start_time.isoformat()
end_iso = end_time.isoformat()

forecast_data = []

for place, (lat, lon) in locations.items():
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&hourly=temperature_2m,precipitation&"
        f"models=ecmwf_seamless,gfs_seamless&start={start_iso}&end={end_iso}&timezone=Asia/Kolkata"
    )
    response = requests.get(url)
    if response.status_code != 200:
        continue

    data = response.json()
    hourly = data.get("hourly", {})
    temps_ecmwf = hourly.get("temperature_2m_ecmwf_seamless", [])
    temps_gfs = hourly.get("temperature_2m_gfs_seamless", [])
    rain_ecmwf = hourly.get("precipitation_ecmwf_seamless", [])
    rain_gfs = hourly.get("precipitation_gfs_seamless", [])

    max_temp_ecmwf = max(temps_ecmwf) if temps_ecmwf else 0.0
    max_temp_gfs = max(temps_gfs) if temps_gfs else 0.0
    total_rain_ecmwf = sum(rain_ecmwf) if rain_ecmwf else 0.0
    total_rain_gfs = sum(rain_gfs) if rain_gfs else 0.0

    confidence = "ECMWF" if abs(max_temp_ecmwf - max_temp_gfs) < 1 and total_rain_ecmwf > total_rain_gfs else "GFS"
    final_temp = max_temp_ecmwf if confidence == "ECMWF" else max_temp_gfs
    final_rain = total_rain_ecmwf if confidence == "ECMWF" else total_rain_gfs
    rainy = "Yes" if final_rain >= 2.5 else "No"

    forecast_data.append({
        "Place": place,
        "ECMWF Max Temp (°C)": round(max_temp_ecmwf, 1),
        "GFS Max Temp (°C)": round(max_temp_gfs, 1),
        "ECMWF Rain (mm)": round(total_rain_ecmwf, 1),
        "GFS Rain (mm)": round(total_rain_gfs, 1),
        "Confidence": confidence,
        "Final Temp (°C)": round(final_temp, 1),
        "Final Rain (mm)": round(final_rain, 1),
        "Rain ≥2.5mm?": rainy
    })

df = pd.DataFrame(forecast_data)

# Highlight summary metrics
chennai_places = ["Nungambakkam", "Meenambakkam", "Sriperumbudur", "Mahabalipuram", "Gummidipoondi", "Cholavaram"]
tn_candidates = [row for row in forecast_data if row["Place"] not in ["Pasighat", "Ooty PTO", "Kodaikanal"]]
tn_max = max(tn_candidates, key=lambda x: x["Final Temp (°C)"]) if tn_candidates else {}

col1, col2 = st.columns(2)
with col1:
    st.metric("🌡️ Chennai Max Temp", f"{df.loc[df['Place'].isin(chennai_places), 'Final Temp (°C)'].max()} °C")
    st.metric("☔ Chennai Rainy Stations", f"{df.loc[df['Place'].isin(chennai_places), 'Rain ≥2.5mm?'].tolist().count('Yes')} / 6")

with col2:
    if tn_max:
        st.metric("🌡️ TN Max Temp", f"{tn_max['Final Temp (°C)']} °C @ {tn_max['Place']}")
    st.metric("⛈️ TN Rainy Stations", f"{df[df['Rain ≥2.5mm?']=='Yes'].shape[0]} / {len(df)}")

st.subheader("📊 Forecast Table")
st.dataframe(df.set_index("Place"))
