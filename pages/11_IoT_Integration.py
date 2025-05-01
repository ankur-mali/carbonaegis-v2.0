import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import random
import plotly.express as px
import plotly.graph_objects as go
from utils.data_manager import init_session_state

# Initialize session state
init_session_state()

# Initialize IoT session states
if 'iot_devices' not in st.session_state:
    st.session_state.iot_devices = []
if 'iot_device_data' not in st.session_state:
    st.session_state.iot_device_data = {}
if 'iot_monitoring_active' not in st.session_state:
    st.session_state.iot_monitoring_active = False
if 'iot_last_update' not in st.session_state:
    st.session_state.iot_last_update = datetime.now()
if 'iot_emissions_saved' not in st.session_state:
    st.session_state.iot_emissions_saved = 0

# Add Carbon Aegis branding
col1, col2 = st.columns([1, 5])
with col1:
    st.image("assets/logo.png", width=100)
with col2:
    st.title("Carbon Aegis - IoT Integration")

st.markdown("""
Connect your IoT devices for real-time emissions monitoring and automatic data collection.
This feature allows for more accurate and timely tracking of energy usage, emissions sources,
and environmental conditions across your facilities.
""")

# Sample IoT device types with their data capabilities
device_types = {
    "Energy Monitor": {
        "description": "Monitors electricity consumption in real-time",
        "metrics": ["kWh consumption", "Peak demand (kW)", "Power factor"],
        "emission_factors": {"kWh consumption": 0.42},  # kg CO2e per kWh
        "data_frequency": "1 minute",
        "connection_methods": ["Wi-Fi", "Ethernet", "LoRaWAN"],
        "image": "assets/energy_monitor.png"
    },
    "HVAC Sensor": {
        "description": "Monitors heating, ventilation, and air conditioning systems",
        "metrics": ["Energy consumption (kWh)", "Temperature (°C)", "Runtime hours"],
        "emission_factors": {"Energy consumption (kWh)": 0.42},  # kg CO2e per kWh
        "data_frequency": "5 minutes",
        "connection_methods": ["Wi-Fi", "Bluetooth", "Zigbee"],
        "image": "assets/hvac_sensor.png"
    },
    "Vehicle Tracker": {
        "description": "Tracks fleet vehicle movement, fuel consumption, and emissions",
        "metrics": ["Fuel consumption (L)", "Distance traveled (km)", "Idle time (min)"],
        "emission_factors": {"Fuel consumption (L)": 2.3},  # kg CO2e per liter diesel
        "data_frequency": "30 seconds",
        "connection_methods": ["4G/LTE", "GPS", "Bluetooth"],
        "image": "assets/vehicle_tracker.png"
    },
    "Smart Meter": {
        "description": "Monitors gas, water, and electricity consumption",
        "metrics": ["Electricity (kWh)", "Natural gas (m³)", "Water (m³)"],
        "emission_factors": {
            "Electricity (kWh)": 0.42,  # kg CO2e per kWh
            "Natural gas (m³)": 2.03,   # kg CO2e per m³
        },
        "data_frequency": "15 minutes",
        "connection_methods": ["Wi-Fi", "Ethernet", "Cellular"],
        "image": "assets/smart_meter.png"
    },
    "Environmental Sensor": {
        "description": "Monitors air quality, temperature, and humidity",
        "metrics": ["CO2 concentration (ppm)", "Temperature (°C)", "Humidity (%)"],
        "emission_factors": {},  # Monitoring only, no direct emissions
        "data_frequency": "10 minutes",
        "connection_methods": ["Wi-Fi", "Bluetooth", "Zigbee"],
        "image": "assets/env_sensor.png"
    },
    "Refrigerant Leak Detector": {
        "description": "Detects and quantifies refrigerant leaks from cooling systems",
        "metrics": ["Refrigerant type", "Leak rate (g/hr)", "System pressure (bar)"],
        "emission_factors": {"Leak rate (g/hr)": 1430},  # kg CO2e per kg of R-134a (GWP=1430)
        "data_frequency": "1 hour",
        "connection_methods": ["Wi-Fi", "Ethernet", "LoRaWAN"],
        "image": "assets/refrigerant_detector.png"
    }
}

# Sidebar for device management
with st.sidebar:
    st.subheader("IoT Device Management")
    
    # Add new device
    st.markdown("### Add New Device")
    with st.form("add_device_form"):
        device_name = st.text_input("Device Name", placeholder="e.g., Main Office Energy Monitor")
        device_type = st.selectbox("Device Type", options=list(device_types.keys()))
        location = st.text_input("Location", placeholder="e.g., Main Office Floor 1")
        connection = st.selectbox("Connection Method", options=device_types[device_type]["connection_methods"])
        
        # Generate a unique device ID
        device_id = f"IOT-{len(st.session_state.iot_devices) + 1:03d}"
        
        submit_button = st.form_submit_button("Add Device")
        
        if submit_button:
            if not device_name or not location:
                st.error("Please fill in all required fields")
            else:
                # Create new device object
                new_device = {
                    "id": device_id,
                    "name": device_name,
                    "type": device_type,
                    "location": location,
                    "connection": connection,
                    "status": "Online",
                    "last_reading": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "added_on": datetime.now().strftime("%Y-%m-%d")
                }
                
                # Add to devices list
                st.session_state.iot_devices.append(new_device)
                
                # Initialize device data
                st.session_state.iot_device_data[device_id] = {
                    "timestamps": [],
                    "metrics": {}
                }
                
                # Initialize metrics for this device type
                for metric in device_types[device_type]["metrics"]:
                    st.session_state.iot_device_data[device_id]["metrics"][metric] = []
                
                st.success(f"Device {device_name} added successfully!")
                st.rerun()
    
    # Manage existing devices
    if st.session_state.iot_devices:
        st.markdown("### Manage Devices")
        
        for i, device in enumerate(st.session_state.iot_devices):
            with st.expander(f"{device['name']} ({device['type']})"):
                st.markdown(f"**ID:** {device['id']}")
                st.markdown(f"**Location:** {device['location']}")
                st.markdown(f"**Status:** {device['status']}")
                st.markdown(f"**Last Reading:** {device['last_reading']}")
                
                if st.button("Remove Device", key=f"remove_{i}"):
                    # Remove device data
                    if device['id'] in st.session_state.iot_device_data:
                        del st.session_state.iot_device_data[device['id']]
                    
                    # Remove device from list
                    st.session_state.iot_devices.remove(device)
                    st.success(f"Device {device['name']} removed")
                    st.rerun()

# Main content area
if not st.session_state.iot_devices:
    # No devices added yet
    st.info("No IoT devices connected yet. Add devices using the sidebar to start monitoring.")
    
    # Show available device types
    st.subheader("Available IoT Device Types")
    
    # Display device types in a grid
    cols = st.columns(2)
    for i, (device_type, details) in enumerate(device_types.items()):
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(device_type)
                st.markdown(f"**Description:** {details['description']}")
                st.markdown("**Metrics:**")
                for metric in details['metrics']:
                    st.markdown(f"- {metric}")
                st.markdown(f"**Data Frequency:** {details['data_frequency']}")
else:
    # Devices are connected, show dashboard
    
    # Live monitoring toggle
    monitoring_status = "Active" if st.session_state.iot_monitoring_active else "Paused"
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"IoT Monitoring Dashboard - {monitoring_status}")
    
    with col2:
        if st.session_state.iot_monitoring_active:
            if st.button("Pause Monitoring", use_container_width=True):
                st.session_state.iot_monitoring_active = False
                st.rerun()
        else:
            if st.button("Start Monitoring", use_container_width=True):
                st.session_state.iot_monitoring_active = True
                st.rerun()
    
    # Summary metrics
    total_devices = len(st.session_state.iot_devices)
    active_devices = sum(1 for d in st.session_state.iot_devices if d['status'] == 'Online')
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Devices", total_devices)
    with col2:
        st.metric("Active Devices", f"{active_devices}/{total_devices}")
    with col3:
        st.metric("Emissions Saved", f"{st.session_state.iot_emissions_saved:.2f} kg CO₂e")
    
    # Generate simulated IoT data if monitoring is active
    if st.session_state.iot_monitoring_active:
        current_time = datetime.now()
        
        # Check if it's time for a new reading (every 10 seconds in this demo)
        if (current_time - st.session_state.iot_last_update).total_seconds() >= 5:
            st.session_state.iot_last_update = current_time
            
            # Update data for each device
            for device in st.session_state.iot_devices:
                device_id = device['id']
                device_type = device['type']
                
                # Add new timestamp
                timestamp = current_time.strftime("%H:%M:%S")
                st.session_state.iot_device_data[device_id]["timestamps"].append(timestamp)
                
                # Limit data history for demo (keep only last 30 readings)
                if len(st.session_state.iot_device_data[device_id]["timestamps"]) > 30:
                    st.session_state.iot_device_data[device_id]["timestamps"] = st.session_state.iot_device_data[device_id]["timestamps"][-30:]
                
                # Generate simulated values for each metric
                for metric in device_types[device_type]["metrics"]:
                    # Generate realistic values based on metric type
                    if "kWh" in metric or "Energy" in metric:
                        # Energy consumption
                        base_value = 5 + random.uniform(-0.5, 0.5)  # kWh around 5 with small fluctuations
                        
                        # Add some daily patterns (higher during work hours)
                        hour = current_time.hour
                        if 9 <= hour <= 17:  # Working hours
                            base_value *= 1.5
                        
                        value = max(0, base_value)
                    elif "Fuel" in metric:
                        # Fuel consumption
                        value = random.uniform(0.8, 2.3)  # Liters
                    elif "Temperature" in metric:
                        # Temperature with gradual changes
                        last_values = st.session_state.iot_device_data[device_id]["metrics"].get(metric, [])
                        if last_values:
                            last_value = last_values[-1]
                            value = last_value + random.uniform(-0.3, 0.3)  # Small temperature change
                            value = max(18, min(25, value))  # Keep between 18-25°C
                        else:
                            value = random.uniform(20, 24)  # Initial temperature
                    elif "CO2" in metric:
                        # CO2 concentration
                        value = random.uniform(400, 800)  # ppm
                    elif "Leak" in metric:
                        # Refrigerant leak
                        value = random.uniform(0, 0.5)  # g/hr - mostly small values
                    else:
                        # Generic values for other metrics
                        value = random.uniform(10, 100)
                    
                    # Store the value
                    st.session_state.iot_device_data[device_id]["metrics"].setdefault(metric, []).append(value)
                    
                    # Limit data history
                    if len(st.session_state.iot_device_data[device_id]["metrics"][metric]) > 30:
                        st.session_state.iot_device_data[device_id]["metrics"][metric] = st.session_state.iot_device_data[device_id]["metrics"][metric][-30:]
                
                # Update last reading timestamp
                device['last_reading'] = current_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # Calculate emissions
                emission_factors = device_types[device_type]["emission_factors"]
                for metric, factor in emission_factors.items():
                    if metric in st.session_state.iot_device_data[device_id]["metrics"]:
                        latest_value = st.session_state.iot_device_data[device_id]["metrics"][metric][-1]
                        emissions = latest_value * factor / 12  # Divide by 12 to simulate 5-min samples per hour
                        
                        # Randomly simulate emission savings through IoT optimizations (5-15%)
                        savings_factor = random.uniform(0.05, 0.15)
                        emissions_saved = emissions * savings_factor
                        st.session_state.iot_emissions_saved += emissions_saved
            
            # Rerun to update the UI
            st.rerun()
    
    # Visualization of IoT data
    if st.session_state.iot_devices:
        selected_device = st.selectbox(
            "Select Device to View Data",
            options=[d['name'] for d in st.session_state.iot_devices],
            index=0
        )
        
        # Get the selected device details
        device = next((d for d in st.session_state.iot_devices if d['name'] == selected_device), None)
        
        if device:
            st.markdown(f"### {selected_device} - {device['type']} Data")
            st.markdown(f"**Location:** {device['location']} | **Status:** {device['status']} | **Last Reading:** {device['last_reading']}")
            
            device_id = device['id']
            device_type = device['type']
            
            if device_id in st.session_state.iot_device_data:
                data = st.session_state.iot_device_data[device_id]
                
                if data["timestamps"]:
                    # Display charts for each metric
                    metric_tabs = st.tabs([metric for metric in device_types[device_type]["metrics"]])
                    
                    for i, metric in enumerate(device_types[device_type]["metrics"]):
                        with metric_tabs[i]:
                            if metric in data["metrics"] and data["metrics"][metric]:
                                # Create dataframe for the metric
                                df = pd.DataFrame({
                                    "Timestamp": data["timestamps"],
                                    metric: data["metrics"][metric]
                                })
                                
                                # Display line chart
                                fig = px.line(df, x="Timestamp", y=metric, markers=True)
                                fig.update_layout(
                                    height=300,
                                    margin=dict(l=20, r=20, t=30, b=20),
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                
                                # Display latest value
                                latest_value = data["metrics"][metric][-1]
                                st.markdown(f"**Latest Reading:** {latest_value:.2f}")
                                
                                # Show emissions if applicable
                                if metric in device_types[device_type]["emission_factors"]:
                                    factor = device_types[device_type]["emission_factors"][metric]
                                    emissions = latest_value * factor
                                    st.markdown(f"**Estimated Emissions:** {emissions:.2f} kg CO₂e/hr")
                            else:
                                st.info(f"No data available for {metric} yet.")
                else:
                    st.info("No data recorded yet. Start monitoring to collect data.")
            else:
                st.error("Device data not found.")
        
        # Show emissions analysis
        st.subheader("Emissions Analysis")
        
        # Create sample emissions data aggregation
        emissions_data = pd.DataFrame({
            "Device": [d['name'] for d in st.session_state.iot_devices],
            "Type": [d['type'] for d in st.session_state.iot_devices],
            "Location": [d['location'] for d in st.session_state.iot_devices],
            "Emissions (kg CO₂e/day)": [
                sum(
                    st.session_state.iot_device_data[d['id']]["metrics"][metric][-1] * factor * 24
                    for metric, factor in device_types[d['type']]["emission_factors"].items()
                    if metric in st.session_state.iot_device_data[d['id']]["metrics"] 
                    and st.session_state.iot_device_data[d['id']]["metrics"][metric]
                ) if d['id'] in st.session_state.iot_device_data else 0
                for d in st.session_state.iot_devices
            ]
        })
        
        if not emissions_data.empty and emissions_data["Emissions (kg CO₂e/day)"].sum() > 0:
            # Create pie chart
            fig = px.pie(
                emissions_data, 
                values="Emissions (kg CO₂e/day)", 
                names="Device",
                title="Emissions Distribution by Device",
                hole=0.4
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Create bar chart by location
            location_emissions = emissions_data.groupby("Location")["Emissions (kg CO₂e/day)"].sum().reset_index()
            fig = px.bar(
                location_emissions,
                x="Location",
                y="Emissions (kg CO₂e/day)",
                title="Emissions by Location",
                color="Emissions (kg CO₂e/day)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Start monitoring to see emissions analysis.")
        
        # IoT data integration with Carbon Aegis
        st.subheader("Integration with Carbon Aegis")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Update Emissions Inventory", use_container_width=True):
                st.success("IoT data has been integrated into your Carbon Aegis emissions inventory.")
        
        with col2:
            if st.button("Schedule Automatic Updates", use_container_width=True):
                st.success("Automatic updates scheduled. IoT data will be synced with your inventory daily.")
        
        st.markdown("""
        **Integration Benefits:**
        
        * Automated data collection reduces manual entry errors
        * Real-time monitoring enables faster detection of issues
        * More granular data improves the accuracy of your emissions inventory
        * Identify opportunities for efficiency improvements and emissions reductions
        * Support for continuous monitoring and reporting
        """)

# Add navigation
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("📊 ESG Dashboard", use_container_width=True):
        st.switch_page("pages/6_ESG_Dashboard.py")
with col2:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")
with col3:
    if st.button("📝 Generate Report", use_container_width=True):
        st.switch_page("pages/3_Report.py")