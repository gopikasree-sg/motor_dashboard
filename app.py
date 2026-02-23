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
# ENTER YOUR THINGSPEAK DETAILS
# ===============================
CHANNEL1_ID = "3271158"
CHANNEL1_READ = "R4ZU1JPB7EJRDB67"

CHANNEL2_ID = "3273029"
CHANNEL2_READ = "C1EDD2ZGBMKAJY52"

# ===============================
# FETCH CHANNEL 1 (RAW SENSOR)
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
rul = latest2["field2"]
oee = latest2["field3"]
severity = int(latest2["field4"])

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
# SENSOR PANEL
# ===============================
st.subheader("📡 Live Sensor Monitoring")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Vibration (mm/s)", vibration)
c2.metric("Temperature (°C)", temperature)
c3.metric("Current (A)", current)
c4.metric("Voltage (V)", voltage)

# ===============================
# PERFORMANCE PANEL
# ===============================
st.subheader("📊 Predictive Indicators")

p1,p2,p3 = st.columns(3)
p1.metric("Health %", health)
p2.metric("Remaining Useful Life (hrs)", rul)
p3.metric("OEE %", oee)

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
# SENSOR TRENDS
# ===============================
st.subheader("📈 Sensor Trends")

fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=df1["created_at"], y=df1["field1"], mode="lines", name="Vibration"))
fig1.add_trace(go.Scatter(x=df1["created_at"], y=df1["field2"], mode="lines", name="Temperature"))
fig1.add_trace(go.Scatter(x=df1["created_at"], y=df1["field3"], mode="lines", name="Current"))
fig1.add_trace(go.Scatter(x=df1["created_at"], y=df1["field4"], mode="lines", name="Voltage"))

st.plotly_chart(fig1, use_container_width=True)

# ===============================
# PERFORMANCE TRENDS
# ===============================
st.subheader("📈 Performance Trends")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=df2["created_at"], y=df2["field1"], mode="lines", name="Health"))
fig2.add_trace(go.Scatter(x=df2["created_at"], y=df2["field2"], mode="lines", name="RUL"))
fig2.add_trace(go.Scatter(x=df2["created_at"], y=df2["field3"], mode="lines", name="OEE"))

st.plotly_chart(fig2, use_container_width=True)