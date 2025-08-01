import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Cell Charging System Dashboard",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .status-good { color: #28a745; }
    .status-warning { color: #ffc107; }
    .status-critical { color: #dc3545; }
    .status-charging { color: #17a2b8; }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for data persistence
if 'cell_data' not in st.session_state:
    st.session_state.cell_data = []
    st.session_state.last_update = datetime.now()

def generate_cell_data():
    """Generate realistic cell charging data"""
    charging_processes = ['CC', 'CV', 'Trickle', 'Fast', 'None']
    statuses = ['Charging', 'Complete', 'Idle', 'Error']
    health_states = ['Excellent', 'Good', 'Warning', 'Critical']
    
    cells = []
    for i in range(1, 9):  # 8 cells
        # Simulate realistic charging behavior
        if i <= 4:  # First 4 cells actively charging
            voltage = round(random.uniform(3.9, 4.2), 2)
            current = round(random.uniform(0.5, 3.5), 1)
            capacity = random.randint(60, 99)
            status = random.choice(['Charging', 'Charging', 'Complete'])
            process = random.choice(['CC', 'CV', 'Fast'])
        else:  # Remaining cells
            voltage = round(random.uniform(3.7, 4.21), 2)
            current = round(random.uniform(0.0, 1.0), 1)
            capacity = random.randint(85, 100)
            status = random.choice(['Complete', 'Idle'])
            process = random.choice(['Trickle', 'None'])
        
        temperature = random.randint(22, 45)
        health = random.choice(health_states) if temperature < 40 else 'Warning'
        
        cells.append({
            'Cell_ID': f'Cell_{i:02d}',
            'Voltage_V': voltage,
            'Current_A': current,
            'Temperature_C': temperature,
            'Capacity_%': capacity,
            'Status': status,
            'Process': process,
            'Health': health,
            'Power_W': round(voltage * current, 1),
            'Last_Update': datetime.now()
        })
    
    return pd.DataFrame(cells)

def get_status_color(status):
    """Return color based on status"""
    colors = {
        'Charging': '#17a2b8',
        'Complete': '#28a745',
        'Idle': '#6c757d',
        'Error': '#dc3545'
    }
    return colors.get(status, '#6c757d')

def get_health_color(health):
    """Return color based on health"""
    colors = {
        'Excellent': '#28a745',
        'Good': '#17a2b8',
        'Warning': '#ffc107',
        'Critical': '#dc3545'
    }
    return colors.get(health, '#6c757d')

def create_gauge_chart(value, title, min_val=0, max_val=100, color='blue'):
    """Create a gauge chart for metrics"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title},
        gauge = {
            'axis': {'range': [None, max_val]},
            'bar': {'color': color},
            'steps': [
                {'range': [0, max_val*0.5], 'color': "lightgray"},
                {'range': [max_val*0.5, max_val*0.8], 'color': "gray"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val*0.9
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def main():
    # Main title
    st.markdown('<h1 class="main-header">🔋 Cell Charging System Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("⚙️ System Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (5s)", value=True)
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.session_state.cell_data = generate_cell_data()
        st.session_state.last_update = datetime.now()
    
    # Generate initial data or refresh
    if len(st.session_state.cell_data) == 0 or auto_refresh:
        st.session_state.cell_data = generate_cell_data()
        st.session_state.last_update = datetime.now()
    
    df = st.session_state.cell_data
    
    # System status indicators
    st.sidebar.markdown("### 📊 System Status")
    active_cells = len(df[df['Status'] == 'Charging'])
    total_power = df['Power_W'].sum()
    avg_temp = df['Temperature_C'].mean()
    avg_capacity = df['Capacity_%'].mean()
    
    st.sidebar.metric("Active Cells", f"{active_cells}/8")
    st.sidebar.metric("Total Power", f"{total_power:.1f} W")
    st.sidebar.metric("Avg Temperature", f"{avg_temp:.1f}°C")
    st.sidebar.metric("Avg Capacity", f"{avg_capacity:.1f}%")
    
    # Charging process filter
    st.sidebar.markdown("### 🔧 Process Filter")
    selected_processes = st.sidebar.multiselect(
        "Select Charging Processes",
        options=df['Process'].unique(),
        default=df['Process'].unique()
    )
    
    # Filter data
    filtered_df = df[df['Process'].isin(selected_processes)]
    
    # Main dashboard layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🔋 Active Charging",
            value=f"{active_cells}",
            delta=f"{active_cells}/8 cells"
        )
    
    with col2:
        st.metric(
            label="⚡ Total Power",
            value=f"{total_power:.1f}W",
            delta="Real-time"
        )
    
    with col3:
        st.metric(
            label="🌡️ Avg Temperature",
            value=f"{avg_temp:.1f}°C",
            delta="Normal" if avg_temp < 35 else "High"
        )
    
    with col4:
        st.metric(
            label="📈 System Efficiency",
            value=f"{avg_capacity:.1f}%",
            delta="Optimal" if avg_capacity > 80 else "Low"
        )
    
    # Charging Process Types Section
    st.markdown("## 🔧 Charging Process Types")
    
    process_col1, process_col2, process_col3, process_col4 = st.columns(4)
    
    with process_col1:
        st.info("**Constant Current (CC)**\nInitial rapid charging phase with constant current flow")
    
    with process_col2:
        st.success("**Constant Voltage (CV)**\nFinal charging phase maintaining constant voltage")
    
    with process_col3:
        st.warning("**Trickle Charge**\nMaintenance charging mode for topped-off cells")
    
    with process_col4:
        st.error("**Fast Charge**\nHigh-current charging protocol for rapid charging")
    
    # Individual Cell Status
    st.markdown("## 📊 Individual Cell Status")
    
    # Create cell status cards in a grid
    for i in range(0, len(filtered_df), 4):
        cols = st.columns(4)
        for j, col in enumerate(cols):
            if i + j < len(filtered_df):
                cell = filtered_df.iloc[i + j]
                with col:
                    status_color = get_status_color(cell['Status'])
                    health_color = get_health_color(cell['Health'])
                    
                    st.markdown(f"""
                    <div style="border: 2px solid {status_color}; border-radius: 10px; padding: 15px; margin: 10px 0;">
                        <h4 style="color: {status_color}; margin: 0;">{cell['Cell_ID']}</h4>
                        <p><strong>Status:</strong> <span style="color: {status_color};">{cell['Status']}</span></p>
                        <p><strong>Process:</strong> {cell['Process']}</p>
                        <p><strong>Voltage:</strong> {cell['Voltage_V']}V</p>
                        <p><strong>Current:</strong> {cell['Current_A']}A</p>
                        <p><strong>Temperature:</strong> {cell['Temperature_C']}°C</p>
                        <p><strong>Capacity:</strong> {cell['Capacity_%']}%</p>
                        <p><strong>Health:</strong> <span style="color: {health_color};">{cell['Health']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Charts Section
    st.markdown("## 📈 System Analytics")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Voltage vs Current scatter plot
        fig_scatter = px.scatter(
            filtered_df, 
            x='Voltage_V', 
            y='Current_A',
            color='Status',
            size='Capacity_%',
            hover_data=['Cell_ID', 'Temperature_C', 'Process'],
            title="Voltage vs Current Analysis"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    with chart_col2:
        # Temperature distribution
        fig_temp = px.histogram(
            filtered_df,
            x='Temperature_C',
            color='Health',
            title="Temperature Distribution by Health",
            nbins=10
        )
        fig_temp.update_layout(height=400)
        st.plotly_chart(fig_temp, use_container_width=True)
    
    # Capacity and Power Charts
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        # Capacity bar chart
        fig_capacity = px.bar(
            filtered_df,
            x='Cell_ID',
            y='Capacity_%',
            color='Status',
            title="Cell Capacity Levels"
        )
        fig_capacity.update_layout(height=400)
        st.plotly_chart(fig_capacity, use_container_width=True)
    
    with chart_col4:
        # Power consumption pie chart
        process_power = filtered_df.groupby('Process')['Power_W'].sum().reset_index()
        fig_pie = px.pie(
            process_power,
            values='Power_W',
            names='Process',
            title="Power Distribution by Process"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed Data Table
    st.markdown("## 📋 Detailed Cell Data")
    
    # Add color coding to the dataframe display
    def highlight_status(val):
        if val == 'Charging':
            return 'background-color: #d1ecf1'
        elif val == 'Complete':
            return 'background-color: #d4edda'
        elif val == 'Error':
            return 'background-color: #f8d7da'
        return ''
    
    styled_df = filtered_df.style.applymap(highlight_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # System Alerts
    st.markdown("## ⚠️ System Alerts")
    
    # Check for alerts
    high_temp_cells = filtered_df[filtered_df['Temperature_C'] > 40]
    low_capacity_cells = filtered_df[filtered_df['Capacity_%'] < 20]
    error_cells = filtered_df[filtered_df['Status'] == 'Error']
    
    if len(high_temp_cells) > 0:
        st.error(f"🌡️ High Temperature Alert: {len(high_temp_cells)} cell(s) running hot!")
        st.write(high_temp_cells[['Cell_ID', 'Temperature_C', 'Status']])
    
    if len(low_capacity_cells) > 0:
        st.warning(f"🔋 Low Capacity Alert: {len(low_capacity_cells)} cell(s) need attention!")
        st.write(low_capacity_cells[['Cell_ID', 'Capacity_%', 'Status']])
    
    if len(error_cells) > 0:
        st.error(f"❌ Error Alert: {len(error_cells)} cell(s) in error state!")
        st.write(error_cells[['Cell_ID', 'Status', 'Health']])
    
    if len(high_temp_cells) == 0 and len(low_capacity_cells) == 0 and len(error_cells) == 0:
        st.success("✅ All systems operating normally!")
    
    # Footer with last update time
    st.markdown("---")
    st.markdown(f"**Last Updated:** {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Auto-refresh mechanism
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
