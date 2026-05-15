import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json

st.set_page_config(page_title="ALS Monitoring Dashboard", layout="wide")

st.markdown("""
<style>
.big-font {
    font-size:24px !important;
    font-weight:600;
}
.metric-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.title("🧠 ALS Monitoring Dashboard")

# Load data from JSON.
data = {
    "total_events": 34,
    "posture_events": 11,
    "breathing_events": 8,
    "medication_events": 7,
    "time_series": [
        {"timestamp": "2024-01-01T08:00:00Z", "event_count": 3},
        {"timestamp": "2024-01-01T10:00:00Z", "event_count": 2},
        {"timestamp": "2024-01-01T12:00:00Z", "event_count": 3},
        {"timestamp": "2024-01-01T13:00:00Z", "event_count": 1},
        {"timestamp": "2024-01-01T14:00:00Z", "event_count": 2},
        {"timestamp": "2024-01-01T15:00:00Z", "event_count": 1},
        {"timestamp": "2024-01-01T16:00:00Z", "event_count": 2},
        {"timestamp": "2024-01-01T18:00:00Z", "event_count": 3},
        {"timestamp": "2024-01-01T19:00:00Z", "event_count": 1},
        {"timestamp": "2024-01-01T20:00:00Z", "event_count": 2},
        {"timestamp": "2024-01-01T21:00:00Z", "event_count": 1},
        {"timestamp": "2024-01-01T22:00:00Z", "event_count": 2},
        {"timestamp": "2024-01-01T23:00:00Z", "event_count": 1}
    ],
    "intervention_trend": {
        "posture": [1,1,1,1,1,1,1,1,1,1],
        "breathing": [1,1,1,1,1,1,1,1,1,1],
        "medication": [2,1,1,1,1,1,1,1,1,1]
    }
}

# ---- KPIs ----
col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Events", data["total_events"])
col2.metric("Posture", data["posture_events"])
col3.metric("Breathing", data["breathing_events"])
col4.metric("Medication", data["medication_events"])

st.divider()

# ---- TIME SERIES ----
st.subheader("📈 Event Timeline")

df = pd.DataFrame(data["time_series"])
df["timestamp"] = pd.to_datetime(df["timestamp"])

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df["timestamp"],
    y=df["event_count"],
    mode='lines+markers',
    line=dict(width=4),
    marker=dict(size=8)
))

fig.update_layout(
    height=450,
    template="plotly_dark",
    margin=dict(l=10, r=10, t=30, b=10),
    xaxis_title="Time",
    yaxis_title="Events",
)

st.plotly_chart(fig, use_container_width=True)

# ---- INTERVENTION TREND ----
st.subheader("📊 Intervention Trends")

trend = data["intervention_trend"]

df_trend = pd.DataFrame({
    "Posture": trend["posture"],
    "Breathing": trend["breathing"],
    "Medication": trend["medication"]
})

fig2 = go.Figure()

fig2.add_trace(go.Scatter(y=df_trend["Posture"], mode='lines+markers', name="Posture", line=dict(width=3)))
fig2.add_trace(go.Scatter(y=df_trend["Breathing"], mode='lines+markers', name="Breathing", line=dict(width=3)))
fig2.add_trace(go.Scatter(y=df_trend["Medication"], mode='lines+markers', name="Medication", line=dict(width=3)))

fig2.update_layout(
    height=450,
    template="plotly_dark",
    margin=dict(l=10, r=10, t=30, b=10),
)

st.plotly_chart(fig2, use_container_width=True)

# ---- DISTRIBUTION ----
st.subheader("📌 Event Distribution")

dist_df = pd.DataFrame({
    "Type": ["Posture", "Breathing", "Medication"],
    "Count": [
        data["posture_events"],
        data["breathing_events"],
        data["medication_events"]
    ]
})

fig3 = px.pie(
    dist_df,
    names="Type",
    values="Count",
    hole=0.5
)

fig3.update_layout(
    height=400,
    template="plotly_dark"
)

st.plotly_chart(fig3, use_container_width=True)