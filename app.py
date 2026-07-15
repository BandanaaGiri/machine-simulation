import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import time

from streamlit_autorefresh import st_autorefresh
from controller import MachineController
from database import Database



# PAGE CONFIGURATION


st.set_page_config(
    page_title="Machine Control & Monitoring",
    page_icon="⚙",
    layout="wide"
)



# CUSTOM UI STYLE


st.markdown("""
<style>
    /* Hide Streamlit default chrome */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Main page - Responsive widescreen layout */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }

    /* Metric containers */
    div[data-testid="metric-container"] {
        border: 1px solid #333842;
        padding: 18px;
        border-radius: 6px;
    }

    .metric-critical div[data-testid="metric-container"] {
        border: 1px solid #ef4444 !important;
        background-color: rgba(239, 68, 68, 0.08);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
    }

    h2 {
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .machine-header {
        border-bottom: 1px solid #333842;
        padding-bottom: 18px;
        margin-bottom: 25px;
    }

    .machine-title {
        font-size: 30px;
        font-weight: 600;
        margin-bottom: 5px;
    }

    .machine-subtitle {
        color: #9aa0aa;
        font-size: 14px;
    }

    .status-running {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #3b8f5a;
    }

    .status-stopped {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #666b75;
    }

    .status-emergency {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #ef4444;
        color: #ef4444;
    }

    /* Industrial table styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #2f333b;
        border-radius: 7px;
        overflow: hidden;
    }

    div[data-testid="stDataFrame"] [role="columnheader"] {
        background-color: #1b1e26;
        color: #aeb5c2;
        font-size: 13px;
        font-weight: 500;
    }

    div[data-testid="stDataFrame"] [role="gridcell"] {
        background-color: #0f1117;
        color: #f2f4f7;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)


# SESSION STATE

if "controller" not in st.session_state:
    st.session_state.controller = MachineController()

if "history" not in st.session_state:
    st.session_state.history = []

if "emergency_logged" not in st.session_state:
    st.session_state.emergency_logged = False


controller = st.session_state.controller
database = Database()


# SIMULATION TICK & AUTO REFRESH

current_status = controller.get_machine_status()

# Detect whether machine is running, cooling, or adjusting pressure
is_cooling = current_status["temperature"] > 25.0
is_depressurizing = abs(current_status["pressure"] - 1.0) > 0.02
needs_update = current_status["running"] or is_cooling or is_depressurizing

# Auto-refresh ticks continuously while machine is active, cooling, or in fault state
if needs_update or current_status["error"]:
    st_autorefresh(
        interval=2000,
        key="machine_loop_tick"
    )

# Advance simulation step (heating or cooling)
if needs_update:
    controller.update_machine()

status = controller.get_machine_status()


# EMERGENCY EVENT LOGGING


if status["error"]:
    if not st.session_state.emergency_logged:
        database.log_event(f"Emergency Stop: {status['error']}")
        st.session_state.emergency_logged = True



# SAVE MACHINE HISTORY


database.log_machine_status(status)

st.session_state.history.append({
    "Time": time.strftime("%H:%M:%S"),
    "RPM": status["speed"],
    "Temperature": status["temperature"],
    "Pressure": status["pressure"]
})

st.session_state.history = st.session_state.history[-60:]



# HEADER


if status["error"]:
    status_badge = '<span class="status-emergency">● FAULT / EMERGENCY</span>'
elif status["running"]:
    status_badge = '<span class="status-running">● RUNNING</span>'
else:
    status_badge = '<span class="status-stopped">● STOPPED</span>'

st.markdown(
    f"""<div class="machine-header">
<div class="machine-title">Machine Control & Monitoring</div>
<div class="machine-subtitle">
MACHINE-01 &nbsp; | &nbsp; Simulation Mode
&nbsp;&nbsp;&nbsp;
{status_badge}
</div>
</div>""",
    unsafe_allow_html=True
)


# SIDEBAR — MACHINE CONTROL

st.sidebar.markdown(
    """
    <div style="
        padding: 8px 0 18px 0;
        border-bottom: 1px solid #333842;
        margin-bottom: 18px;
    ">
        <div style="
            font-size: 20px;
            font-weight: 600;
            letter-spacing: 0.4px;
        ">
            MACHINE CONTROL
        </div>
        <div style="
            color: #9aa0aa;
            font-size: 13px;
            margin-top: 6px;
        ">
            MACHINE-01
        </div>
        <div style="
            color: #777d87;
            font-size: 12px;
            margin-top: 2px;
        ">
            Simulation Mode
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

is_running = status["running"]
has_error = bool(status["error"])

st.sidebar.markdown(
    """
    <div style="
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        color: #8f96a1;
        margin-bottom: 10px;
    ">
        CONTROL
    </div>
    """,
    unsafe_allow_html=True
)

col_s1, col_s2 = st.sidebar.columns(2)

with col_s1:
    if st.button("START", use_container_width=True, disabled=(is_running or has_error or status["temperature"] >= 75.0)):
        controller.start_machine()
        database.log_event("Machine Started")
        st.session_state.emergency_logged = False
        st.rerun()

with col_s2:
    if st.button("STOP", use_container_width=True, disabled=(not is_running)):
        controller.stop_machine()
        database.log_event("Machine Stopped Normally")
        st.rerun()

# Fault reset button appears when a fault is present
if has_error:
    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    if st.sidebar.button("🔄 RESET FAULT / ALARM", type="primary", use_container_width=True):
        controller.reset_fault()
        st.session_state.emergency_logged = False
        database.log_event("Fault Acknowledged & Reset by Operator")
        st.rerun()

st.sidebar.divider()



# SPEED CONTROL


st.sidebar.markdown(
    """
    <div style="
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        color: #8f96a1;
        margin-bottom: 5px;
    ">
        SPEED CONTROL
    </div>
    """,
    unsafe_allow_html=True
)

speed = st.sidebar.slider(
    "RPM",
    min_value=0,
    max_value=3000,
    value=status["speed"],
    step=100,
    disabled=(not is_running or has_error)
)

if is_running and speed != status["speed"]:
    old_speed = status["speed"]
    controller.change_speed(speed)
    database.log_event(f"Speed Changed: {old_speed} → {speed} RPM")

st.sidebar.divider()



# NAVIGATION


st.sidebar.markdown(
    """
    <div style="
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 1px;
        color: #8f96a1;
        margin-bottom: 8px;
    ">
        NAVIGATION
    </div>
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Machine Data",
        "Events & Alerts",
        "Reports",
        "System Information"
    ],
    label_visibility="collapsed"
)

st.sidebar.markdown(
    """
    <div style="
        border-top: 1px solid #333842;
        margin-top: 18px;
        padding-top: 15px;
        font-size: 11px;
        color: #777d87;
        line-height: 1.7;
    ">
        <div>System: Online</div>
        <div>Monitoring: Active</div>
        <div>Database: SQLite</div>
    </div>
    """,
    unsafe_allow_html=True
)


if page == "Dashboard":

    # STATUS SUMMARY
  

    st.subheader("Current Machine Status")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Machine State",
            "RUNNING" if status["running"] else "STOPPED"
        )

    with col2:
        st.metric(
            "Speed",
            f"{status['speed']} RPM"
        )

    with col3:
        if status["temperature"] >= 75.0:
            st.markdown('<div class="metric-critical">', unsafe_allow_html=True)
            st.metric(
                "Temperature",
                f"{status['temperature']:.1f} °C",
                delta="CRITICAL TEMP",
                delta_color="inverse"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.metric("Temperature", f"{status['temperature']:.1f} °C")

    with col4:
        st.metric(
            "Pressure",
            f"{status['pressure']:.2f} bar"
        )



    # SAFETY STATUS


    temperature = status["temperature"]

    st.subheader("System Status")

    if status["error"]:
        st.error(f"EMERGENCY: {status['error']}")
    elif temperature >= 75.0:
        st.warning(f"CRITICAL TEMPERATURE — {temperature:.1f} °C")
    elif temperature >= 60.0:
        st.warning(f"TEMPERATURE WARNING — {temperature:.1f} °C")
    else:
        st.success("SYSTEM NORMAL")



    # LIVE MONITORING (3-COLUMN PINNED-RANGE CHARTS)


    st.subheader("Live Monitoring")

    if st.session_state.history:

        df = pd.DataFrame(st.session_state.history)
        df["Time"] = pd.to_datetime(df["Time"], format="%H:%M:%S")

        base_chart_layout = dict(
            height=260,
            margin=dict(l=10, r=10, t=20, b=10),
            showlegend=False,
            xaxis=dict(tickformat="%H:%M:%S")
        )

        # 1. Temperature Chart (Pinned 15–100°C)
        temperature_fig = go.Figure()
        temperature_fig.add_hrect(
            y0=60, y1=75,
            fillcolor="orange", opacity=0.08,
            line_width=0
        )
        temperature_fig.add_hline(
            y=75,
            line_dash="dash",
            line_color="#EF4444",
            line_width=1.5,
            annotation_text="Trip (75°C)",
            annotation_position="top left",
            annotation_font=dict(size=10, color="#EF4444")
        )
        temperature_fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df["Temperature"],
                mode="lines",
                name="Temperature",
                line=dict(width=2.5, color="#FF8C42")
            )
        )
        temperature_fig.update_layout(
            **base_chart_layout,
            yaxis=dict(title="°C", range=[15, 100])
        )

        # 2. RPM Chart (Pinned 0–3200 RPM)
        rpm_fig = go.Figure()
        rpm_fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df["RPM"],
                mode="lines",
                name="RPM",
                line=dict(width=2.5, color="#4C9AFF"),
                fill="tozeroy",
                fillcolor="rgba(76, 154, 255, 0.08)"
            )
        )
        rpm_fig.update_layout(
            **base_chart_layout,
            yaxis=dict(title="RPM", range=[0, 3200])
        )

        # 3. Pressure Chart (Pinned 0.5–2.0 bar)
        pressure_fig = go.Figure()
        pressure_fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df["Pressure"],
                mode="lines",
                name="Pressure",
                line=dict(width=2.5, color="#4CAF50"),
                fill="tozeroy",
                fillcolor="rgba(76, 175, 80, 0.08)"
            )
        )
        pressure_fig.update_layout(
            **base_chart_layout,
            yaxis=dict(title="bar", range=[0.5, 2.0])
        )

        ch1, ch2, ch3 = st.columns(3)

        with ch1:
            st.caption("Temperature")
            st.plotly_chart(temperature_fig, use_container_width=True)

        with ch2:
            st.caption("Machine Speed")
            st.plotly_chart(rpm_fig, use_container_width=True)

        with ch3:
            st.caption("Pressure")
            st.plotly_chart(pressure_fig, use_container_width=True)

    else:
        st.caption("Waiting for machine data...")


    # EVENTS & HISTORY (SIDE-BY-SIDE TABLES)


    st.divider()

    tbl_col1, tbl_col2 = st.columns(2)

    with tbl_col1:
        st.subheader("Machine Events")
        events = database.get_events(limit=20)
        if not events.empty:
            st.dataframe(
                events,
                use_container_width=True,
                hide_index=True,
                height=380,
                column_config={
                    "timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                    "event": st.column_config.TextColumn("Event Description")
                }
            )
        else:
            st.caption("No machine events recorded.")

    with tbl_col2:
        st.subheader("Machine History")
        logs = database.get_logs(limit=50)
        if not logs.empty:
            logs["running"] = logs["running"].map({
                1: "RUNNING",
                0: "STOPPED"
            })
            st.dataframe(
                logs,
                use_container_width=True,
                hide_index=True,
                height=380,
                column_config={
                    "timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
                    "running": st.column_config.TextColumn("Status", width="small"),
                    "speed": st.column_config.NumberColumn("Speed", format="%d RPM"),
                    "temperature": st.column_config.ProgressColumn(
                        "Temp (°C)",
                        min_value=20,
                        max_value=100,
                        format="%.1f °C"
                    ),
                    "pressure": st.column_config.NumberColumn("Pressure", format="%.2f bar"),
                    "error": st.column_config.TextColumn("Fault")
                }
            )
        else:
            st.caption("No machine history available.")


    # FOOTER


    st.divider()

    st.caption(
        "MACHINE-01  |  Simulation Mode  |  "
        "Automatic monitoring: Active while machine is running or cooling"
    )

elif page == "Machine Data":

    st.subheader("Machine Data")
    st.caption("Historical machine readings stored in the SQLite database.")

    logs = database.get_logs(limit=200)

    if not logs.empty:
        logs["running"] = logs["running"].map({
            1: "RUNNING",
            0: "STOPPED"
        })

        st.dataframe(
            logs,
            use_container_width=True,
            hide_index=True
        )

        csv_data = logs.to_csv(index=False)

        st.download_button(
            "Download Machine Data CSV",
            data=csv_data,
            file_name="machine_data.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No machine data available yet.")


elif page == "Events & Alerts":

    st.subheader("Events & Alerts")

    events = database.get_events(limit=200)

    if not events.empty:
        st.dataframe(
            events,
            use_container_width=True,
            hide_index=True
        )

        csv_data = events.to_csv(index=False)

        st.download_button(
            "Download Events CSV",
            data=csv_data,
            file_name="machine_events.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("No machine events recorded yet.")


elif page == "Reports":

    st.subheader("Reports")
    st.caption("Export machine information for analysis or record keeping.")

    logs = database.get_logs(limit=500)
    events = database.get_events(limit=500)

    st.markdown("### Machine Status Data")

    if not logs.empty:
        logs_display = logs.copy()
        logs_display["running"] = logs_display["running"].map({
            1: "RUNNING",
            0: "STOPPED"
        })

        st.download_button(
            "Download Status CSV",
            data=logs_display.to_csv(index=False),
            file_name="machine_status_report.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.caption("No status data available.")

    st.markdown("### Machine Events")

    if not events.empty:
        st.download_button(
            "Download Events CSV",
            data=events.to_csv(index=False),
            file_name="machine_events_report.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.caption("No event data available.")

    st.markdown("### Full Machine Report")

    if not logs.empty or not events.empty:
        report_parts = []

        if not logs.empty:
            report_parts.append(
                "MACHINE STATUS DATA\n\n"
                + logs.to_csv(index=False)
            )

        if not events.empty:
            report_parts.append(
                "\n\nMACHINE EVENTS\n\n"
                + events.to_csv(index=False)
            )

        full_report = "\n".join(report_parts)

        st.download_button(
            "Download Full Report",
            data=full_report,
            file_name="machine_full_report.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.caption("No report data available yet.")


elif page == "System Information":

    st.subheader("System Information")
    st.caption("Configuration and software components of MACHINE-01.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            **Machine Configuration**

            - Machine ID: `MACHINE-01`
            - Operating Mode: `Simulation`
            - Monitoring Interval: `2 seconds`
            - Speed Range: `0–3000 RPM`
            - Temperature Unit: `°C`
            - Pressure Unit: `bar`
            """
        )

    with col2:
        st.markdown(
            """
            **Software Components**

            - Interface: `Streamlit`
            - Language: `Python`
            - Database: `SQLite`
            - Visualization: `Plotly`
            - Control Architecture: `Python OOP`
            - Machine Communication: `Simulated`
            """
        )

    st.divider()

    st.markdown("### Safety System")

    if status["error"]:
        st.error(f"Active Safety Condition: {status['error']}")
    else:
        st.success("Safety monitoring is active. No current emergency condition.")