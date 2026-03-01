import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Industrial Motor SCADA", layout="wide")

# Auto refresh every 10 seconds
st_autorefresh(interval=10000, key="refresh")

st.title("🏭 Industrial Motor Predictive Maintenance Dashboard")

# ===============================
# THINGSPEAK DETAILS
# ===============================
CHANNEL1_ID = "3271158"
CHANNEL1_READ = "R4ZU1JPB7EJRDB67"

CHANNEL2_ID = "3273029"
CHANNEL2_READ = "C1EDD2ZGBMKAJY52"

# ===============================
# FETCH CHANNEL 1 (CORE METRICS)
# ===============================
url1 = f"https://api.thingspeak.com/channels/{CHANNEL1_ID}/feeds.json?api_key={CHANNEL1_READ}&results=100"
data1 = requests.get(url1).json()
df1 = pd.DataFrame(data1["feeds"])

df1["created_at"] = pd.to_datetime(df1["created_at"])

for col in df1.columns:
    if "field" in col:
        df1[col] = pd.to_numeric(df1[col], errors="coerce")

# ===============================
# FETCH CHANNEL 2 (ANALYTICS)
# ===============================
url2 = f"https://api.thingspeak.com/channels/{CHANNEL2_ID}/feeds.json?api_key={CHANNEL2_READ}&results=100"
data2 = requests.get(url2).json()
df2 = pd.DataFrame(data2["feeds"])

df2["created_at"] = pd.to_datetime(df2["created_at"])

for col in df2.columns:
    if "field" in col:
        df2[col] = pd.to_numeric(df2[col], errors="coerce")

# ===============================
# LATEST VALUES
# ===============================
latest1 = df1.iloc[-1]
latest2 = df2.iloc[-1]

vibration = latest1["field1"]
temperature = latest1["field2"]
current = latest1["field3"]
voltage = latest1["field4"]

health = latest2["field1"]
degradation = latest2["field2"]
anomaly_flag = latest2["field3"]
predictive_health = latest2["field4"]
oee = latest2["field5"]
rul = latest2["field6"]
power_kw = latest2["field7"]
anomaly_score = latest2["field8"]

severity = int(anomaly_flag)

# ===============================
# FAULT & RECOMMENDATION ENGINE
# ===============================
fault = "Normal Operation"
location = "No fault detected"
recommendation = "Continue routine monitoring"
priority = "Low"

if severity >= 5:
    fault = "Critical Multi-Component Degradation"
    location = "Bearing + Winding System"
    recommendation = "Immediate shutdown. Inspect bearings, insulation, shaft alignment and lubrication system."
    priority = "Emergency"

elif severity == 4:
    fault = "Bearing Failure Risk"
    location = "Drive End Bearing"
    recommendation = "Schedule urgent bearing inspection and lubrication."
    priority = "High"

elif severity == 3:
    fault = "Overcurrent Condition"
    location = "Motor Winding Circuit"
    recommendation = "Check load torque, insulation resistance and supply imbalance."
    priority = "Medium"

elif severity == 2:
    fault = "Thermal Stress"
    location = "Stator Core"
    recommendation = "Inspect cooling fan and ventilation airflow."
    priority = "Low"

# ===============================
# STATUS BANNER
# ===============================
if severity >= 4:
    st.error("🔴 CRITICAL MOTOR CONDITION")
elif severity == 3:
    st.warning("🟠 WARNING CONDITION")
else:
    st.success("🟢 MOTOR RUNNING NORMALLY")

# ===============================
# LIVE METRICS PANEL
# ===============================
st.subheader("📡 Core Operational Metrics")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Vibration (mm/s)", vibration)
c2.metric("Temperature (°C)", temperature)
c3.metric("Current (A)", current)
c4.metric("Voltage (V)", voltage)

st.subheader("📊 Analytics Layer")

p1,p2,p3,p4 = st.columns(4)
p1.metric("Health Index", health)
p2.metric("OEE %", oee)
p3.metric("RUL (hrs)", rul)
p4.metric("Anomaly Score", anomaly_score)

# ===============================
# FAULT PANEL
# ===============================
st.subheader("⚠ Fault Diagnosis & Recommendation")

f1,f2 = st.columns(2)

with f1:
    st.info(f"Fault Type: {fault}")
    st.info(f"Location: {location}")
    st.info(f"Priority: {priority}")

with f2:
    st.warning("Recommended Maintenance Action")
    st.write(recommendation)

# ===============================
# INDIVIDUAL TREND CHARTS
# ===============================
st.subheader("📈 Individual Sensor Trends")

def single_trend(df, x, y, title):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x], y=df[y], mode="lines", name=title))
    fig.update_layout(title=title, xaxis_title="Time", yaxis_title=title)
    st.plotly_chart(fig, use_container_width=True)

# Core Metrics Trends
single_trend(df1, "created_at", "field1", "Dynamic Vibration Signal")
single_trend(df1, "created_at", "field2", "Temperature")
single_trend(df1, "created_at", "field3", "Phase Load Current (A)")
single_trend(df1, "created_at", "field4", "Supply Integrity Voltage")
single_trend(df1, "created_at", "field5", "Rotational Drive Speed")
single_trend(df1, "created_at", "field7", "Real-Time Power Draw")
single_trend(df1, "created_at", "field8", "Motor Utilization Ratio")

# Analytics Trends
st.subheader("📈 Predictive & Performance Trends")

single_trend(df2, "created_at", "field1", "Health Index")
single_trend(df2, "created_at", "field2", "Degradation Rate")
single_trend(df2, "created_at", "field4", "Predictive Health")
single_trend(df2, "created_at", "field5", "OEE (%)")
single_trend(df2, "created_at", "field6", "Remaining Useful Life")
single_trend(df2, "created_at", "field8", "Anomaly Score")