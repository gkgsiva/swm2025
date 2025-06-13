
import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="Weather Contest Dashboard", layout="wide")
st.title("🌤️ SWM Weather Contest Dashboard")
st.caption("Based on ECMWF and GFS models | Period: 8:30 AM to 8:30 AM IST")

# Full list of locations
locations = {
    "Nungambakkam": [
        13.0632,
        80.2495
    ],
    "Meenambakkam": [
        12.9941,
        80.1808
    ],
    "Sriperumbudur": [
        13.03,
        79.9495
    ],
    "Mahabalipuram": [
        12.6208,
        80.193
    ],
    "Gummidipoondi": [
        13.4072,
        80.1085
    ],
    "Cholavaram": [
        13.215,
        80.1833
    ],
    "Tiruttani": [
        13.1806,
        79.6042
    ],
    "Vellore": [
        12.9165,
        79.1325
    ],
    "Tiruvannamalai": [
        12.2253,
        79.0747
    ],
    "Karur": [
        10.9601,
        78.0766
    ],
    "Namakkal": [
        11.2196,
        78.1675
    ],
    "Tiruchirappalli": [
        10.7905,
        78.7047
    ],
    "Tirupattur": [
        12.4987,
        78.5708
    ],
    "Tiruchengode": [
        11.3855,
        77.8945
    ],
    "Erode": [
        11.341,
        77.7172
    ],
    "Coimbatore": [
        11.0168,
        76.9558
    ],
    "Pollachi": [
        10.658,
        77.006
    ],
    "Valparai": [
        10.3269,
        76.9515
    ],
    "Dharmapuri": [
        12.1211,
        78.158
    ],
    "Tirunelveli": [
        8.7139,
        77.7567
    ],
    "Palayamkottai": [
        8.7302,
        77.7384
    ],
    "Tenkasi": [
        8.9591,
        77.315
    ],
    "Sankarankovil": [
        9.1715,
        77.5456
    ],
    "Papanasam": [
        10.7658,
        79.1341
    ],
    "Kodaikanal": [
        10.2381,
        77.4892
    ],
    "Ooty PTO": [
        11.4102,
        76.695
    ],
    "Pasighat": [
        28.0667,
        95.3333
    ],
    "Mumbai": [
        19.076,
        72.8777
    ],
    "Kolkata": [
        22.5726,
        88.3639
    ],
    "Goa": [
        15.2993,
        74.124
    ],
    "Ahmedabad": [
        23.0225,
        72.5714
    ],
    "Hyderabad": [
        17.385,
        78.4867
    ],
    "Nagpur": [
        21.1458,
        79.0882
    ],
    "Bengaluru": [
        12.9716,
        77.5946
    ],
    "Pune": [
        18.5204,
        73.8567
    ],
    "Jaipur": [
        26.9124,
        75.7873
    ]
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

st.subheader("📊 Forecast Table")
if not df.empty:
    st.dataframe(df.set_index("Place"), use_container_width=True)

    chennai_places = ["Nungambakkam", "Meenambakkam", "Sriperumbudur", "Mahabalipuram", "Gummidipoondi", "Cholavaram"]
    tn_hills = ["Kodaikanal", "Ooty PTO"]
    tn_max_pool = [p for p in df["Place"] if p not in tn_hills and "Tamil Nadu" not in p and p not in ["Pasighat", "Mumbai", "Kolkata", "Goa", "Ahmedabad", "Hyderabad", "Nagpur", "Bengaluru", "Pune", "Jaipur"]]
    tn_max_df = df[df["Place"].isin(tn_max_pool)]
    tn_max = tn_max_df.loc[tn_max_df["Final Temp (°C)"].idxmax()] if not tn_max_df.empty else None

    col1, col2 = st.columns(2)
    with col1:
        st.metric("🌡️ Chennai Max Temp", f"{df.loc[df['Place'].isin(chennai_places), 'Final Temp (°C)'].max()} °C")
        st.metric("☔ Chennai Rainy Stations", f"{df.loc[df['Place'].isin(chennai_places), 'Rain ≥2.5mm?'].tolist().count('Yes')} / 6")
    with col2:
        if tn_max is not None:
            st.metric("🌡️ TN Max Temp", f"{tn_max['Final Temp (°C)']} °C @ {tn_max['Place']}")
        st.metric("⛈️ TN Rainy Stations", f"{df[df['Rain ≥2.5mm?']=='Yes'].shape[0]} / {len(df)}")

    st.subheader("📈 Temperature Comparison")
    st.bar_chart(df.set_index("Place")[["ECMWF Max Temp (°C)", "GFS Max Temp (°C)"]])

    st.subheader("🌧️ Rainfall Comparison")
    st.bar_chart(df.set_index("Place")[["ECMWF Rain (mm)", "GFS Rain (mm)"]])
else:
    st.warning("⚠️ No forecast data available. Check API or internet connection.")
