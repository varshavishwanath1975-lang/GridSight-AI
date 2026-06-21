import streamlit as st
from PIL import Image
import pandas as pd
import os
import random
import streamlit.components.v1 as components

from detector import detect_vehicles
from ocr_reader import read_number_plate
from violation_logic import classify_traffic
from database import save_record
from report_generator import generate_pdf
from save_history import save_traffic_history
from prediction import predict_future_vehicle_count
from streamlit_autorefresh import st_autorefresh
from realtime_predictor import get_realtime_prediction

st.set_page_config(page_title="GridSight AI", layout="wide")
st_autorefresh(interval=5000, key="realtime_refresh")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #020617, #0f172a, #111827);
    color: white;
}
.hero {
    background: linear-gradient(135deg, rgba(14,165,233,0.28), rgba(30,64,175,0.35));
    padding: 26px;
    border-radius: 24px;
    border: 1px solid rgba(56,189,248,0.4);
    box-shadow: 0 0 30px rgba(56,189,248,0.18);
}
.hero h1 {
    font-size: 44px;
    margin: 0;
    font-weight: 900;
}
.hero p {
    color: #dbeafe;
    font-size: 17px;
}
.kpi-card {
    background: rgba(15,23,42,0.95);
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 18px;
    padding: 18px;
}
.kpi-label {
    color: #94a3b8;
    font-size: 13px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 900;
}
.alert-card {
    background: rgba(15,23,42,0.95);
    border: 1px solid rgba(148,163,184,0.25);
    border-radius: 16px;
    padding: 14px;
    margin-bottom: 10px;
}
.badge-red {
    color: #fecaca;
    background: #7f1d1d;
    padding: 5px 10px;
    border-radius: 999px;
    float: right;
}
.badge-orange {
    color: #fde68a;
    background: #78350f;
    padding: 5px 10px;
    border-radius: 999px;
    float: right;
}
.badge-green {
    color: #bbf7d0;
    background: #14532d;
    padding: 5px 10px;
    border-radius: 999px;
    float: right;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🚦 GridSight AI Command Center</h1>
    <p>AI traffic detection, congestion forecasting, Bengaluru hotspot monitoring and enforcement intelligence.</p>
</div>
""", unsafe_allow_html=True)

LOCATION_COORDS = {
    "Silk Board Junction": [12.9177, 77.6237],
    "Majestic": [12.9767, 77.5713],
    "BTM Layout": [12.9166, 77.6101],
    "Electronic City": [12.8452, 77.6602],
    "KR Market": [12.9627, 77.5761],
    "Hebbal Flyover": [13.0358, 77.5970],
    "Whitefield": [12.9698, 77.7500],
    "Manyata Tech Park": [13.0420, 77.6216],
    "Marathahalli": [12.9569, 77.7011],
    "Indiranagar": [12.9784, 77.6408],
    "Koramangala": [12.9352, 77.6245],
    "Jayanagar": [12.9250, 77.5938],
    "Yeshwanthpur": [13.0250, 77.5340],
    "Tin Factory": [12.9965, 77.6692],
    "Kengeri": [12.9170, 77.4838],
    "Banashankari": [12.9181, 77.5736],
    "Rajajinagar": [12.9915, 77.5550],
    "MG Road": [12.9758, 77.6068],
    "Domlur": [12.9609, 77.6387],
    "Bellandur": [12.9304, 77.6784],
}

def safe_number(series):
    return pd.to_numeric(
        series.astype(str)
        .str.replace("%", "", regex=False)
        .str.replace("Unknown", "0", regex=False),
        errors="coerce"
    ).fillna(0)

def ensure_sample_data():
    os.makedirs("database", exist_ok=True)
    file_path = "database/violations.csv"

    if os.path.exists(file_path):
        return

    rows = [
        ["KA01AB1234", "Silk Board Junction", "Traffic Congestion", "High", 24, "70%", 32, 32, 40, 48, "📈 Increasing", "92%", "95%", "HIGH", 5, 4, 2, "2026-06-21 10:00:00"],
        ["KA05MN6789", "Majestic", "Traffic Congestion", "Medium", 18, "60%", 25, 25, 31, 38, "📈 Increasing", "88%", "76%", "MEDIUM", 3, 2, 1, "2026-06-21 10:05:00"],
        ["KA03CD4587", "Whitefield", "Normal Traffic", "Low", 9, "30%", 14, 14, 18, 22, "➡ Stable", "86%", "44%", "LOW", 1, 0, 0, "2026-06-21 10:10:00"],
        ["KA51EF9021", "Electronic City", "Traffic Congestion", "Medium", 15, "55%", 22, 22, 28, 35, "📈 Increasing", "89%", "68%", "MEDIUM", 3, 2, 1, "2026-06-21 10:15:00"],
        ["KA02GH7744", "Hebbal Flyover", "Normal Traffic", "Low", 11, "35%", 16, 16, 20, 27, "➡ Stable", "84%", "52%", "LOW", 1, 0, 0, "2026-06-21 10:20:00"]
    ]

    cols = [
        "Vehicle Number", "Location", "Traffic Status", "Severity", "Vehicle Count",
        "Current Risk Index", "Predicted Vehicle Count", "15 Min Forecast",
        "30 Min Forecast", "60 Min Forecast", "Prediction Trend",
        "Prediction Confidence", "Predicted Risk Index", "Enforcement Priority",
        "Police Officers Required", "Barricades Recommended",
        "Patrol Vehicles Required", "Timestamp"
    ]

    pd.DataFrame(rows, columns=cols).to_csv(file_path, index=False)

def load_records():
    ensure_sample_data()
    df = pd.read_csv("database/violations.csv", on_bad_lines="skip")

    required_cols = {
        "Vehicle Number": "UNKNOWN",
        "Location": "Silk Board Junction",
        "Traffic Status": "Normal Traffic",
        "Severity": "Low",
        "Vehicle Count": 10,
        "Current Risk Index": "40%",
        "Predicted Vehicle Count": 15,
        "15 Min Forecast": 15,
        "30 Min Forecast": 20,
        "60 Min Forecast": 25,
        "Prediction Trend": "➡ Stable",
        "Prediction Confidence": "85%",
        "Predicted Risk Index": "50%",
        "Enforcement Priority": "LOW",
        "Police Officers Required": 1,
        "Barricades Recommended": 0,
        "Patrol Vehicles Required": 0,
        "Timestamp": "2026-06-21 10:00:00"
    }

    for col, default in required_cols.items():
        if col not in df.columns:
            df[col] = default

    numeric_cols = [
        "Vehicle Count",
        "Current Risk Index",
        "Predicted Vehicle Count",
        "15 Min Forecast",
        "30 Min Forecast",
        "60 Min Forecast",
        "Predicted Risk Index",
        "Prediction Confidence",
        "Police Officers Required",
        "Barricades Recommended",
        "Patrol Vehicles Required"
    ]

    for col in numeric_cols:
        df[col + " Numeric"] = safe_number(df[col])

    return df

def build_location_data(df):
    summary = (
        df.groupby("Location")
        .agg(
            vehicles=("Vehicle Count Numeric", "mean"),
            f15=("15 Min Forecast Numeric", "mean"),
            f30=("30 Min Forecast Numeric", "mean"),
            f60=("60 Min Forecast Numeric", "mean"),
            risk=("Predicted Risk Index Numeric", "mean"),
            confidence=("Prediction Confidence Numeric", "mean"),
            cases=("Location", "count")
        )
        .reset_index()
    )

    data = []

    for idx, (loc, coords) in enumerate(LOCATION_COORDS.items()):
        row = summary[summary["Location"] == loc]
        lat, lng = coords

        if not row.empty:
            risk = float(row.iloc[0]["risk"])
            f15 = int(row.iloc[0]["f15"])
            f30 = int(row.iloc[0]["f30"])
            f60 = int(row.iloc[0]["f60"])
            cases = int(row.iloc[0]["cases"])
            confidence = int(row.iloc[0]["confidence"])
        else:
            risk = random.randint(20, 55)
            f15 = random.randint(8, 20)
            f30 = f15 + random.randint(3, 8)
            f60 = f30 + random.randint(4, 12)
            cases = 0
            confidence = random.randint(75, 90)

        risk = max(5, min(100, risk + random.randint(-5, 8)))

        if risk >= 80:
            label = "Critical"
            color = "#ef4444"
        elif risk >= 50:
            label = "Moderate"
            color = "#f59e0b"
        else:
            label = "Normal"
            color = "#22c55e"

        data.append({
            "id": idx,
            "location": loc,
            "lat": lat,
            "lng": lng,
            "risk": round(risk, 1),
            "risk_label": label,
            "color": color,
            "forecast_15": f15,
            "forecast_30": f30,
            "forecast_60": f60,
            "cases": cases,
            "confidence": confidence
        })

    return data

def show_simple_google_map(location_data):
    api_key = st.secrets.get("GOOGLE_MAPS_API_KEY", "")

    if not api_key:
        st.warning("Google Maps API key not set in Streamlit secrets. Showing location table instead.")
        st.dataframe(pd.DataFrame(location_data), use_container_width=True)
        return

    markers = ""

    for item in location_data:
        markers += f"""
        new google.maps.Marker({{
            position: {{lat: {item['lat']}, lng: {item['lng']}}},
            map: map,
            title: "{item['location']}",
            label: "{item['risk_label'][0]}"
        }});

        new google.maps.Circle({{
            strokeColor: "{item['color']}",
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: "{item['color']}",
            fillOpacity: 0.30,
            map: map,
            center: {{lat: {item['lat']}, lng: {item['lng']}}},
            radius: {int(500 + item['risk'] * 18)}
        }});
        """

    html = f"""
    <html>
    <head>
    <script src="https://maps.googleapis.com/maps/api/js?key={api_key}"></script>
    </head>
    <body style="margin:0;">
        <div id="map" style="height:620px;width:100%;border-radius:18px;"></div>
        <script>
        const map = new google.maps.Map(document.getElementById("map"), {{
            zoom: 11,
            center: {{lat: 12.9716, lng: 77.5946}},
            mapTypeId: "roadmap"
        }});

        const trafficLayer = new google.maps.TrafficLayer();
        trafficLayer.setMap(map);

        {markers}
        </script>
    </body>
    </html>
    """

    components.html(html, height=650)

with st.sidebar:
    st.header("⚙️ Control Panel")

    location = st.selectbox("📍 Select Traffic Location", list(LOCATION_COORDS.keys()))

    event_type = st.selectbox(
        "🎪 Event Scenario",
        ["None", "Festival", "Sports Event", "Political Rally", "Concert", "Construction Activity"]
    )

    input_mode = st.radio("Input Mode", ["Upload Image", "Camera Capture"])

df = load_records()
location_data = build_location_data(df)
sorted_locations = sorted(location_data, key=lambda x: x["risk"], reverse=True)

critical = sum(1 for x in location_data if x["risk"] >= 80)
moderate = sum(1 for x in location_data if 50 <= x["risk"] < 80)
avg_risk = round(sum(x["risk"] for x in location_data) / len(location_data), 1)
avg_conf = round(sum(x["confidence"] for x in location_data) / len(location_data), 1)

st.divider()

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Bengaluru Zones</div><div class="kpi-value">{len(location_data)}</div></div>', unsafe_allow_html=True)

with k2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Critical Zones</div><div class="kpi-value">{critical}</div></div>', unsafe_allow_html=True)

with k3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Moderate Zones</div><div class="kpi-value">{moderate}</div></div>', unsafe_allow_html=True)

with k4:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">Average Risk</div><div class="kpi-value">{avg_risk}%</div></div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚦 Detection", "🗺️ Command Center", "📄 Records"])

with tab1:
    st.subheader("🚦 Live Detection")

    uploaded_file = None
    camera_image = None

    if input_mode == "Upload Image":
        uploaded_file = st.file_uploader("Upload Traffic Image", type=["jpg", "jpeg", "png"])
    else:
        camera_image = st.camera_input("📷 Capture Live Traffic Image")

    input_file = uploaded_file if uploaded_file is not None else camera_image

    if input_file is not None:
        os.makedirs("uploads", exist_ok=True)
        image_path = "uploads/input.jpg"

        with open(image_path, "wb") as f:
            f.write(input_file.getbuffer())

        image = Image.open(image_path)

        c1, c2 = st.columns(2)

        with c1:
            st.image(image, caption="Input Image", width="stretch")

        results, vehicle_count = detect_vehicles(image_path)

        save_traffic_history(location, vehicle_count)
        future_prediction = predict_future_vehicle_count(location)

        detected_image = results[0].plot()

        with c2:
            st.image(detected_image, caption="Detection Output", width="stretch")

        traffic_status, severity = classify_traffic(vehicle_count)
        current_risk = min(vehicle_count * 4, 100)

        event_extra = {
            "None": 0,
            "Festival": 12,
            "Sports Event": 15,
            "Political Rally": 18,
            "Concert": 14,
            "Construction Activity": 10
        }

        predicted_count = int(vehicle_count * 1.4 + event_extra[event_type])

        if future_prediction is not None:
            predicted_count = int((predicted_count + future_prediction) / 2)

        f15 = predicted_count
        f30 = int(predicted_count * 1.25)
        f60 = int(predicted_count * 1.5)
        predicted_risk = min(predicted_count * 4, 100)

        if predicted_risk >= 80:
            priority = "HIGH"
            officers = 5
            barricades = 4
            patrol = 2
        elif predicted_risk >= 50:
            priority = "MEDIUM"
            officers = 3
            barricades = 2
            patrol = 1
        else:
            priority = "LOW"
            officers = 1
            barricades = 0
            patrol = 0

        all_texts, plates = read_number_plate(image_path)
        plate = plates[0] if plates else "UNKNOWN"

        st.subheader("🔮 Prediction Result")

        p1, p2, p3, p4 = st.columns(4)
        p1.metric("Vehicles", vehicle_count)
        p2.metric("15 Min", f15)
        p3.metric("30 Min", f30)
        p4.metric("60 Min", f60)

        st.metric("Predicted Risk", f"{predicted_risk}%")
        st.success(f"Detected Plate: {plate}")
        st.info(f"Priority: {priority} | Officers: {officers} | Barricades: {barricades} | Patrol: {patrol}")

        report = {
            "Vehicle Number": plate,
            "Location": location,
            "Event Scenario": event_type,
            "Traffic Status": traffic_status,
            "Severity": severity,
            "Vehicle Count": vehicle_count,
            "Current Risk Index": f"{current_risk}%",
            "Predicted Vehicle Count": predicted_count,
            "15 Min Forecast": f15,
            "30 Min Forecast": f30,
            "60 Min Forecast": f60,
            "Prediction Trend": "📈 Increasing",
            "Prediction Confidence": "92%",
            "Predicted Risk Index": f"{predicted_risk}%",
            "Heat Level": "Critical" if predicted_risk >= 80 else "Moderate" if predicted_risk >= 50 else "Normal",
            "Enforcement Priority": priority,
            "Police Officers Required": officers,
            "Barricades Recommended": barricades,
            "Patrol Vehicles Required": patrol,
            "Recommended Action": "Deploy resources based on AI risk score.",
            "Confidence": 95
        }

        saved_report = save_record(report)

        pdf_path = generate_pdf(saved_report)

        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                "⬇️ Download Evidence Report PDF",
                pdf_file,
                file_name="traffic_evidence_report.pdf",
                mime="application/pdf"
            )

    else:
        st.info("Upload or capture a traffic image to start detection.")

with tab2:
    st.subheader("🗺️ Bengaluru Google Map Command Center")

    map_col, side_col = st.columns([1.4, 1])

    with map_col:
        show_simple_google_map(location_data)

    with side_col:
        st.subheader("🏆 Risk Leaderboard")

        for item in sorted_locations[:8]:
            if item["risk"] >= 80:
                badge = "badge-red"
                label = "Critical"
            elif item["risk"] >= 50:
                badge = "badge-orange"
                label = "Moderate"
            else:
                badge = "badge-green"
                label = "Normal"

            st.markdown(f"""
            <div class="alert-card">
                <b>{item["location"]}</b>
                <span class="{badge}">{label}</span><br>
                Risk: <b>{item["risk"]}%</b><br>
                15 Min: {item["forecast_15"]} |
                30 Min: {item["forecast_30"]} |
                60 Min: {item["forecast_60"]}
            </div>
            """, unsafe_allow_html=True)

    st.subheader("📊 Risk by Location")
    chart_df = pd.DataFrame(location_data)[["location", "risk"]].set_index("location")
    st.bar_chart(chart_df)

    st.subheader("📈 Forecast Trend by Location")
    forecast_df = pd.DataFrame(location_data)[
        ["location", "forecast_15", "forecast_30", "forecast_60"]
    ].set_index("location")
    st.line_chart(forecast_df)

with tab3:
    st.subheader("📄 Stored Traffic Records")
    st.dataframe(load_records(), use_container_width=True)
