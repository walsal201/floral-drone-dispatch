import streamlit as st
import requests
import json
import logging
import random
from datetime import datetime
import pandas as pd
import pydeck as pdk

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Default Configuration for Child Lost Agency
CONFIG = {
    "trackingApiUrl": "https://mock-tracking-api.com/locations",
    "droneControlApiUrl": "https://mock-drone-control.com/deploy",
    "reportingApiUrl": "https://mock-reporting.com/report",
    "droneSwarmSize": 20,
    "maxFlightRadius": 2000,
    "recoveryThreshold": 0.90,
    "alertWebhookUrl": "https://mock-webhook.com/tracking-alert"
}

# Sidebar controls
st.sidebar.header("🛠 Tracking Controls")
swarm_size = st.sidebar.slider("Drone Swarm Size", min_value=5, max_value=50, value=CONFIG["droneSwarmSize"])
recovery_threshold = st.sidebar.slider("Recovery Threshold", min_value=0.5, max_value=1.0, value=CONFIG["recoveryThreshold"], step=0.01)
alert_filter = st.sidebar.selectbox("Filter Alert Type", options=["All", "lost_child", "battery_low", "out_of_zone"])

CONFIG["droneSwarmSize"] = swarm_size
CONFIG["recoveryThreshold"] = recovery_threshold

# Simulation functions for Child Lost Agency
def get_lost_children_locations():
    children = []
    for i in range(random.randint(1, 3)):
        alert_type = random.choice(['lost_child', 'battery_low', 'out_of_zone'])
        lat = random.uniform(-60, 60)
        lon = random.uniform(-150, 150)
        battery = random.uniform(10, 100)
        children.append({
            "device_id": f"DEV-{random.randint(1000,9999)}",
            "child_name": f"Child {i+1}",
            "alert_type": alert_type,
            "latitude": lat,
            "longitude": lon,
            "battery_level": battery,
            "last_seen": datetime.now().isoformat()
        })
    return children

def calculate_drone_path(child):
    start_lat, start_lon = 0.0, 0.0  # Drone base
    target_lat, target_lon = child['latitude'], child['longitude']
    distance = ((target_lat - start_lat)**2 + (target_lon - start_lon)**2)**0.5 * 111000
    path = f"Drone path from base (0,0) to ({target_lat},{target_lon}), distance: {distance:.2f} meters"
    return path, distance

def prepare_tracking_protocol(alert_type):
    if alert_type == 'lost_child':
        return {
            "trackingMode": "emergency_search",
            "dronePayload": "camera_high_res",
            "approachDistance": 5,
            "cameraEnabled": True,
            "safetyProtocol": "child_safe_approach"
        }
    elif alert_type == 'battery_low':
        return {
            "trackingMode": "battery_monitor",
            "dronePayload": "camera_standard",
            "approachDistance": 10,
            "cameraEnabled": True,
            "safetyProtocol": "low_power_mode"
        }
    else:  # out_of_zone
        return {
            "trackingMode": "zone_monitoring",
            "dronePayload": "camera_standard",
            "approachDistance": 15,
            "cameraEnabled": True,
            "safetyProtocol": "boundary_alert"
        }

def execute_tracking(protocol, child):
    success = random.random() > (1 - CONFIG['recoveryThreshold'])
    return "located" if success else "searching"

def log_tracking_results(child, protocol, result):
    return {
        "timestamp": datetime.now().isoformat(),
        "device_id": child['device_id'],
        "child_name": child['child_name'],
        "alert_type": child['alert_type'],
        "tracking_mode": protocol['trackingMode'],
        "latitude": child['latitude'],
        "longitude": child['longitude'],
        "battery_level": child['battery_level'],
        "result": result
    }

def send_tracking_report(results):
    report = {
        "mission_id": f"tracking-{int(datetime.now().timestamp())}",
        "results": results
    }
    logger.info(f"Sending tracking report: {json.dumps(report)}")
    return report

def drone_tracking_job():
    children = get_lost_children_locations()
    tracking_results = []

    for child in children:
        path, distance = calculate_drone_path(child)
        protocol = prepare_tracking_protocol(child['alert_type'])
        result = execute_tracking(protocol, child)
        log_entry = log_tracking_results(child, protocol, result)
        tracking_results.append(log_entry)

    report = send_tracking_report(tracking_results)
    return children, tracking_results, report

def simulate_alert_webhook():
    alert = {
        "deviceId": f"DEV-{random.randint(1000,9999)}",
        "alertType": random.choice(['LOST_CHILD', 'BATTERY_LOW', 'OUT_OF_ZONE']),
        "latitude": random.uniform(-60, 60),
        "longitude": random.uniform(-150, 150),
        "timestamp": datetime.now().isoformat(),
        "batteryLevel": random.uniform(10, 100),
        "alertSeverity": random.choice(['HIGH', 'MEDIUM', 'LOW'])
    }
    return alert

# Main UI
st.set_page_config(layout="wide")
st.title("👶 Child Lost Agency - Smart Tracking System")
st.markdown("Mini drones with cameras track lost children using GPS chips in bracelets, clothing, shoes, rings, and ear pieces. Client signup available for new parents.")

# Client Registration Section
st.subheader("📝 Client Registration")

with st.form("client_registration_form"):
    col1, col2 = st.columns(2)
    with col1:
        parent_name = st.text_input("Parent/Guardian Full Name")
        parent_email = st.text_input("Email Address")
        parent_phone = st.text_input("Phone Number")
        child_name = st.text_input("Child Full Name")
    with col2:
        child_birthdate = st.date_input("Child Date of Birth")
        service_package = st.selectbox("Service Package", ["Basic - 2 Devices", "Standard - 4 Devices", "Premium - 6 Devices"])
        device_types = st.multiselect("Select Device Types", ["Bracelet", "Shoe Chip", "Clothing Tag", "Ring", "Ear Pearls"])
        emergency_contact = st.text_input("Emergency Contact Name")
        emergency_phone = st.text_input("Emergency Contact Phone")

    special_instructions = st.text_area("Special Instructions or Medical Information")
    registered = st.form_submit_button("📋 Register Client")

if registered:
    client_id = f"CL-{random.randint(10000,99999)}"
    st.success(f"✅ Client {client_id} registered successfully!")
    st.markdown(f"**Client ID:** {client_id}")
    st.markdown(f"**Service Package:** {service_package}")
    st.markdown(f"**Devices:** {', '.join(device_types)}")

# Manual Alert Input
st.subheader("🚨 Manual Alert Authorization")

with st.form("manual_alert_form"):
    col1, col2 = st.columns(2)
    with col1:
        manual_lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=24.7136)
        manual_alert_type = st.selectbox("Alert Type", ["lost_child", "battery_low", "out_of_zone"])
        manual_child_name = st.text_input("Child Name", value="Manual Child")
    with col2:
        manual_lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=46.6753)
        manual_device_id = st.text_input("Device ID", value=f"DEV-{random.randint(1000,9999)}")
        manual_battery = st.slider("Battery Level", min_value=0.0, max_value=100.0, value=50.0)

    alert_submitted = st.form_submit_button("🚁 Deploy Drone")

if alert_submitted:
    manual_child = {
        "device_id": manual_device_id,
        "child_name": manual_child_name,
        "alert_type": manual_alert_type,
        "latitude": manual_lat,
        "longitude": manual_lon,
        "battery_level": manual_battery,
        "last_seen": datetime.now().isoformat()
    }

    path, distance = calculate_drone_path(manual_child)
    protocol = prepare_tracking_protocol(manual_alert_type)
    result = execute_tracking(protocol, manual_child)
    log_entry = log_tracking_results(manual_child, protocol, result)

    st.success(f"✅ Drone deployed for {manual_child_name} ({manual_alert_type}).")
    st.markdown(f"**Drone Path:** {path}")
    st.markdown(f"**Tracking Mode:** {protocol['trackingMode']}")
    st.markdown(f"**Result:** {result}")
    st.json(log_entry)

# Simulate Alert Webhook
st.subheader("🔗 Simulate Tracking Alert Webhook")
if st.button("📡 Trigger Random Alert"):
    alert = simulate_alert_webhook()
    st.info("🚨 Alert Received!")
    st.json(alert)

    # Simulate response
    child = {
        "device_id": alert["deviceId"],
        "child_name": f"Child {alert['deviceId'][-4:]}",
        "alert_type": alert["alertType"].lower(),
        "latitude": alert["latitude"],
        "longitude": alert["longitude"],
        "battery_level": alert["batteryLevel"],
        "last_seen": alert["timestamp"]
    }

    protocol = prepare_tracking_protocol(child['alert_type'])
    result = execute_tracking(protocol, child)
    log_entry = log_tracking_results(child, protocol, result)

    st.success(f"🚁 Drone deployed automatically for {child['child_name']}.")
    st.markdown(f"**Alert Severity:** {alert['alertSeverity']}")
    st.markdown(f"**Tracking Result:** {result}")

# Auto Tracking Button
if st.button("🚀 Run Drone Tracking Patrol"):
    children, results, report = drone_tracking_job()

    if alert_filter != "All":
        results = [r for r in results if r["alert_type"] == alert_filter]

    st.subheader("👶 Children Detected")
    st.json(children)

    st.subheader("📊 Tracking Results")
    df_results = pd.DataFrame(results)
    st.dataframe(df_results)

    located = sum(1 for r in results if r["result"] == "located")
    total = len(results)
    success_rate = (located / total) * 100 if total > 0 else 0
    st.metric(label="📍 Recovery Success Rate", value=f"{success_rate:.1f}%", delta=f"{located}/{total} children")

    st.subheader("🗺️ Child Locations Map")
    df_map = df_results.copy()
    df_map['color'] = df_map['alert_type'].map(lambda x: [255, 0, 0] if x == 'lost_child' else [255, 255, 0] if x == 'battery_low' else [0, 255, 0])
    df_map['size'] = df_map['result'].map(lambda x: 200 if x == 'located' else 100)

    st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/light-v11',
        initial_view_state=pdk.ViewState(
            latitude=0,
            longitude=0,
            zoom=1.5,
            pitch=30,
        ),
        layers=[
            pdk.Layer(
                'ScatterplotLayer',
                data=df_map,
                get_position='[longitude, latitude]',
                get_color='color',
                get_radius='size',
                pickable=True,
                opacity=0.8,
            ),
            pdk.Layer(
                "LineLayer",
                data=df_map,
                get_source_position="[0, 0]",
                get_target_position="[longitude, latitude]",
                get_color='[0, 0, 255]',
                get_width=2,
                pickable=True,
            )
        ],
        tooltip={"text": "Child: {child_name}\nAlert: {alert_type}\nResult: {result}\nBattery: {battery_level:.1f}%\nLat: {latitude}\nLon: {longitude}"}
    ))

    st.subheader("📤 Export Tracking Results")
    csv = df_results.to_csv(index=False).encode('utf-8')
    json_data = df_results.to_json(orient="records", indent=2)

    st.download_button("Download CSV", csv, "tracking_results.csv", "text/csv")
    st.download_button("Download JSON", json_data, "tracking_results.json", "application/json")

    st.subheader("📝 Tracking Report")
    st.json(report)
