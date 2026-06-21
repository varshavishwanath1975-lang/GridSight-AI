import streamlit as st
from PIL import Image
import pandas as pd
import os

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

st.title("🚦 GridSight AI – Traffic Intelligence & Congestion Forecasting Platform")

with st.sidebar:
    st.header("⚙️ Control Panel")

    location = st.selectbox(
        "📍 Select Traffic Location",
        [
            "Silk Board Junction",
            "Majestic",
            "BTM Layout",
            "Electronic City",
            "KR Market",
            "Hebbal Flyover",
            "Whitefield",
            "Manyata Tech Park"
        ]
    )

    event_type = st.selectbox(
        "🎪 Event Scenario",
        [
            "None",
            "Festival",
            "Sports Event",
            "Political Rally",
            "Concert",
            "Construction Activity"
        ]
    )

    realtime_mode = st.checkbox("🟢 Enable Real-Time Prediction Mode", value=True)

    input_mode = st.radio("Input Mode", ["Upload Image", "Camera Capture"])

if realtime_mode:
    st_autorefresh(interval=5000, key="realtime_refresh")

# =========================
# REAL-TIME LIVE PANEL
# =========================

st.subheader("🟢 Live Real-Time Prediction Engine")

p15_live, p30_live, p60_live, live_trend = get_realtime_prediction(location)

if p15_live is not None:
    live_risk = min(p60_live * 4, 100)

    live_status, live_severity = classify_traffic(p60_live)

    l1, l2, l3, l4, l5 = st.columns(5)

    l1.metric("Next 15 Min", p15_live)
    l2.metric("Next 30 Min", p30_live)
    l3.metric("Next 60 Min", p60_live)
    l4.metric("Live Risk", f"{live_risk}%")
    l5.metric("Live Trend", live_trend)

    if live_risk >= 80:
        st.error(f"🚨 Real-time alert: Critical congestion predicted at {location}.")
    elif live_risk >= 50:
        st.warning(f"⚠️ Real-time alert: Moderate congestion predicted at {location}.")
    else:
        st.success(f"✅ Real-time alert: Traffic stable at {location}.")

else:
    st.info(
        f"Collect at least 3 traffic samples for **{location}** to activate real-time prediction."
    )

st.divider()

uploaded_file = None
camera_image = None

if input_mode == "Upload Image":
    uploaded_file = st.file_uploader("Upload Traffic Image", type=["jpg", "jpeg", "png"])
else:
    camera_image = st.camera_input("📷 Capture Live Traffic Image")

input_file = uploaded_file if uploaded_file is not None else camera_image

if input_file is not None:

    image_path = "uploads/input.jpg"

    os.makedirs("uploads", exist_ok=True)

    with open(image_path, "wb") as f:
        f.write(input_file.getbuffer())

    image = Image.open(image_path)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📷 Input Image")
        st.image(image, width="stretch")

    results, vehicle_count = detect_vehicles(image_path)

    save_traffic_history(location, vehicle_count)
    future_prediction = predict_future_vehicle_count(location)

    detected_image = results[0].plot()

    with col2:
        st.subheader("🚗 YOLOv8 Detection Output")
        st.image(detected_image, width="stretch")

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

    rule_prediction = int(vehicle_count * 1.4 + event_extra[event_type])

    if future_prediction is not None:
        predicted_count = int((rule_prediction + future_prediction) / 2)
        model_status = "ACTIVE"
    else:
        predicted_count = rule_prediction
        model_status = "COLLECTING DATA"

    forecast_15 = predicted_count
    forecast_30 = int(predicted_count * 1.25)
    forecast_60 = int(predicted_count * 1.5)

    if forecast_60 > forecast_15:
        trend = "📈 Increasing"
    elif forecast_60 < forecast_15:
        trend = "📉 Decreasing"
    else:
        trend = "➡ Stable"

    history_file = "database/traffic_history.csv"

    if os.path.exists(history_file):
        history_len = len(pd.read_csv(history_file))
    else:
        history_len = 0

    confidence = min(95, 70 + history_len)

    predicted_status, predicted_severity = classify_traffic(predicted_count)
    predicted_risk = min(predicted_count * 4, 100)

    if predicted_risk >= 80:
        heat_level = "🔴 Critical"
        priority = "HIGH"
        officers = 5
        barricades = 4
        patrol_vehicles = 2
        recommendation = (
            "Deploy additional traffic police, activate diversion routes, "
            "restrict illegal parking, and monitor continuously."
        )
    elif predicted_risk >= 50:
        heat_level = "🟡 Moderate"
        priority = "MEDIUM"
        officers = 3
        barricades = 2
        patrol_vehicles = 1
        recommendation = (
            "Monitor the zone, restrict roadside parking, "
            "and keep diversion support ready."
        )
    else:
        heat_level = "🟢 Safe"
        priority = "LOW"
        officers = 1
        barricades = 0
        patrol_vehicles = 0
        recommendation = "No immediate enforcement action required. Continue passive monitoring."

    st.subheader("📊 Current Traffic Intelligence")

    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Vehicles", vehicle_count)
    a2.metric("Current Status", traffic_status)
    a3.metric("Severity", severity)
    a4.metric("Current Risk", f"{current_risk}%")

    st.subheader("🔮 Real-Time Multi-Horizon Prediction")

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("15 Min Forecast", forecast_15)
    b2.metric("30 Min Forecast", forecast_30)
    b3.metric("60 Min Forecast", forecast_60)
    b4.metric("Confidence", f"{confidence}%")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Forecast Status", predicted_status)
    c2.metric("Predicted Risk", f"{predicted_risk}%")
    c3.metric("Model Status", model_status)
    c4.metric("Trend", trend)

    st.info(f"📍 Location: {location}")
    st.info(f"🎪 Event Scenario: {event_type}")
    st.info(f"🔥 Heat Level: {heat_level}")

    if priority == "HIGH":
        st.error(f"🚨 Enforcement Priority: {priority}")
    elif priority == "MEDIUM":
        st.warning(f"⚠️ Enforcement Priority: {priority}")
    else:
        st.success(f"✅ Enforcement Priority: {priority}")

    st.subheader("🚓 Smart Resource Allocation")

    r1, r2, r3 = st.columns(3)
    r1.metric("Police Officers", officers)
    r2.metric("Barricades", barricades)
    r3.metric("Patrol Vehicles", patrol_vehicles)

    st.success(f"Recommended Action: {recommendation}")

    st.subheader("🔍 OCR Number Plate Detection")

    all_texts, plates = read_number_plate(image_path)

    with st.expander("View OCR Raw Text"):
        if all_texts:
            for text in all_texts:
                st.write(f"- {text}")
        else:
            st.write("No OCR text detected.")

    if plates:
        selected_plate = plates[0]
        st.success(f"Detected Number Plate: {selected_plate}")
    else:
        selected_plate = "UNKNOWN"
        st.warning("No clear number plate detected.")

    st.subheader("🤖 AI Executive Summary")

    st.write(
        f"At {location}, the system detected {vehicle_count} vehicles. "
        f"The current traffic condition is {traffic_status} with {current_risk}% risk. "
        f"Considering {event_type} and live traffic history, the system forecasts {forecast_15}, "
        f"{forecast_30}, and {forecast_60} vehicles for the next 15, 30, and 60 minutes. "
        f"The trend is {trend}. Enforcement priority is {priority}."
    )

    st.subheader("📄 Evidence Report")

    report = {
        "Vehicle Number": selected_plate,
        "Location": location,
        "Event Scenario": event_type,
        "Traffic Status": predicted_status,
        "Severity": predicted_severity,
        "Vehicle Count": vehicle_count,
        "Current Risk Index": f"{current_risk}%",
        "Predicted Vehicle Count": predicted_count,
        "15 Min Forecast": forecast_15,
        "30 Min Forecast": forecast_30,
        "60 Min Forecast": forecast_60,
        "Prediction Trend": trend,
        "Prediction Confidence": f"{confidence}%",
        "Predicted Risk Index": f"{predicted_risk}%",
        "Heat Level": heat_level,
        "Enforcement Priority": priority,
        "Police Officers Required": officers,
        "Barricades Recommended": barricades,
        "Patrol Vehicles Required": patrol_vehicles,
        "Recommended Action": recommendation,
        "Confidence": 95
    }

    report = save_record(report)

    st.success("Evidence record generated successfully")

    with st.expander("View Full Evidence Report", expanded=True):
        for key, value in report.items():
            st.write(f"**{key}:** {value}")

    pdf_path = generate_pdf(report)

    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="⬇️ Download Evidence Report PDF",
            data=pdf_file,
            file_name="traffic_evidence_report.pdf",
            mime="application/pdf"
        )

else:
    st.info("Upload or capture a traffic image to add a new real-time traffic sample.")