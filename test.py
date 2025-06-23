import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import graphviz # You might need to install this: pip install graphviz streamlit-agraph

# --- Page Configuration (Set Wide Layout) ---
st.set_page_config(layout="wide", page_title="Onboarding Assessment Dashboard")

# --- Custom CSS (Basic Styling - Needs Significant Enhancement for Exact Match) ---
# This CSS is a starting point. You'll need to inspect the elements in your browser
# and add more specific rules (classes, ids) to match the image precisely.
st.markdown("""
<style>
/* --- General --- */
.stApp {
    /* background-color: #f0f2f6; /* Light grey background */
}

/* --- Top Metric Cards --- */
/* Streamlit's st.metric doesn't easily allow icons on the right or custom backgrounds like the image */
/* We can use st.columns and style divs inside, or accept st.metric's default look */
/* Example: Styling metric containers (adjust selector if needed) */
div[data-testid="stMetric"] {
    background-color: #e8f5e9; /* Light green-ish background example */
    border: 1px solid #c8e6c9;
    padding: 15px;
    border-radius: 5px;
    text-align: center; /* Center align content */
    margin-bottom: 10px; /* Add space below cards */
}

/* Style individual metric labels and values if needed */
div[data-testid="stMetric"] label {
    font-weight: bold;
    color: #388e3c; /* Darker green label */
}

div[data-testid="stMetric"] div.stMetricValue {
    font-size: 2em; /* Larger value font */
    font-weight: bold;
    color: #1b5e20; /* Even darker green value */
}

/* --- Custom styling for Decline/Red cards (needs more specific selectors) --- */
/* You would need to add CSS classes or target specific columns/elements */
/* .decline-metric { background-color: #ffebee; border: 1px solid #ffcdd2; } */
/* .decline-metric label { color: #d32f2f; } */
/* .decline-metric div.stMetricValue { color: #b71c1c; } */


/* --- Data Quality Bar --- */
/* Streamlit's st.progress is simple. For a custom look, use HTML/CSS */
.stProgress > div > div > div > div {
     background-image: linear-gradient(to right, #4caf50, #8bc34a, #ffeb3b, #ff9800, #f44336); /* Example gradient */
}
.custom-progress-bar {
    width: 100%;
    background-color: #e0e0e0;
    border-radius: 5px;
    height: 10px; /* Adjust height */
    margin-bottom: 10px;
}
.custom-progress-value {
    width: 70%; /* Example value - make dynamic */
    background-color: #2196F3; /* Blue color */
    height: 10px;
    border-radius: 5px;
}

/* --- Key Info Boxes (Data Quality section) --- */
.key-info-box {
    background-color: #f5f5f5; /* Light grey */
    border: 1px solid #eeeeee;
    padding: 10px;
    border-radius: 4px;
    text-align: center;
    font-size: 0.9em;
    margin-bottom: 5px;
}

/* --- Section Headers --- */
h2 {
    color: #424242; /* Dark grey header */
    border-bottom: 2px solid #e0e0e0;
    padding-bottom: 5px;
    margin-top: 20px;
}

/* --- Legend --- */
.legend-item {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
}
.legend-color-box {
    width: 15px;
    height: 15px;
    margin-right: 8px;
    border: 1px solid #ccc;
}
</style>
""", unsafe_allow_html=True)

# --- Dashboard Title ---
st.title("Onboarding Assessment: [COMPANY NAME]") # Placeholder

# --- Row 1: Key Metrics ---
st.markdown("---") # Separator line
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Using st.metric - limited styling options built-in
    st.metric(label="✅ Credit Score", value="686")
    # To get the exact look, you'd need custom HTML/CSS within the column

with col2:
    st.metric(label="❌ Trading", value="11 mths")
    # You'd apply a different CSS style for 'decline' appearance if using custom HTML

with col3:
    st.metric(label="❌ Industry", value="Construction Services")

with col4:
    st.metric(label="❌ A.I. Recommendation", value="Decline")
    # Add the small red bar below 'Decline' using HTML/CSS if needed
    st.markdown('<div style="width: 60%; height: 5px; background-color: red; margin-top: 5px; border-radius: 2px;"></div>', unsafe_allow_html=True)

# --- Row 2: Data Quality ---
st.markdown("---")
st.subheader("📊 Data Quality")

# Custom HTML progress bar (example)
# st.markdown('<div class="custom-progress-bar"><div class="custom-progress-value"></div></div>', unsafe_allow_html=True)
# Or use Streamlit's simpler progress bar
st.progress(75) # Example value

# Key Info Boxes below the bar
col_dq1, col_dq2, col_dq3, col_dq4, col_dq5, col_dq6 = st.columns(6)
with col_dq1:
    st.markdown('<div class="key-info-box">Credit Enquiries (12mths): <strong>2</strong></div>', unsafe_allow_html=True)
with col_dq2:
    st.markdown('<div class="key-info-box">Director Dereg/Struck: <strong>0</strong></div>', unsafe_allow_html=True)
with col_dq3:
    st.markdown('<div class="key-info-box">Director Adverse: <strong>0</strong></div>', unsafe_allow_html=True)
with col_dq4:
    st.markdown('<div class="key-info-box">Total Past Due: <strong>$0</strong></div>', unsafe_allow_html=True) # Assuming $0 from image value 50?
with col_dq5:
    st.markdown('<div class="key-info-box">Owing 61 to 90: <strong>$0</strong></div>', unsafe_allow_html=True)
with col_dq6:
    st.markdown('<div class="key-info-box">Owing 90+: <strong>$0</strong></div>', unsafe_allow_html=True)


# --- Row 3: Related Entities, Score Gauge, Risk Factors ---
st.markdown("---")
col_ent, col_charts, col_risk = st.columns([1.5, 2, 1.5]) # Adjust column ratios as needed

with col_ent:
    st.subheader("🔗 Related Entities")

    # --- Network Graph (using Graphviz) ---
    # Create a simple graph
    graph = graphviz.Digraph()
    graph.attr(rankdir='TB') # Top to bottom layout
    graph.node('Entity1', 'NAME REMOVED\n(Main Company)', shape='box', style='filled', fillcolor='lightblue')
    graph.node('Entity2', 'NAME REMOVED', shape='ellipse', style='filled', fillcolor='lightcoral')
    graph.node('Entity3', 'NAME REMOVED', shape='ellipse', style='filled', fillcolor='lightcoral')

    graph.edge('Entity1', 'Entity2', label=' Owns')
    graph.edge('Entity1', 'Entity3', label=' Related To') # Example relationship
    st.graphviz_chart(graph)

    # Placeholder if Graphviz isn't installed/configured
    # st.image("https://via.placeholder.com/300x200.png?text=Related+Entities+Graph", caption="Network Graph Placeholder")


with col_charts:
    st.subheader("📊 Score & Ownership")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        # --- Donut Chart (Ownership) ---
        ownership_data = {'labels': ['Ownership', 'Other'], 'values': [100, 0]} # Example data
        fig_donut = go.Figure(data=[go.Pie(labels=ownership_data['labels'],
                                            values=ownership_data['values'],
                                            hole=.6, # Makes it a donut
                                            marker_colors=['#17becf', '#e0e0e0'], # Cyan and grey
                                            textinfo='label+percent',
                                            insidetextorientation='radial')])
        fig_donut.update_layout(title_text='Ownership Structure', showlegend=False, height=300, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
         # --- Gauge Chart (Score) ---
        score_value = 686
        delta_value = 186 # From the image ▲186
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = score_value,
            delta = {'reference': score_value - delta_value, 'increasing': {'color': "green"}}, # Calculate reference based on delta
            gauge = {'axis': {'range': [0, 1000]}, # Adjusted range based on image
                     'bar': {'color': "darkblue"}, # Color of the value bar
                     'steps' : [
                         {'range': [0, 400], 'color': "#f44336"}, # Red
                         {'range': [400, 600], 'color': "#ff9800"}, # Orange
                         {'range': [600, 800], 'color': "#ffeb3b"}, # Yellow
                         {'range': [800, 1000], 'color': "#4caf50"}], # Green
                     'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': score_value}}, # Shows current value marker
            domain = {'x': [0, 1], 'y': [0, 1]}))

        fig_gauge.update_layout(title_text='Credit Score Gauge', height=300, margin=dict(t=40, b=0, l=0, r=0))
        st.plotly_chart(fig_gauge, use_container_width=True)


with col_risk:
    st.subheader("⚠️ Risk Factors")

    # --- Radar Chart ---
    # Match categories from the image
    categories = ['Enquiries', 'Time in Business', 'Credit Score', 'Trade Payments', 'Director Adverse', 'Online Presence', 'Industry']
    # Example values - Replace with actual data
    values = [3, 7, 8, 5, 9, 4, 6] # Scaled 0-10 for example

    fig_radar = go.Figure()

    fig_radar.add_trace(go.Scatterpolar(
          r=values,
          theta=categories,
          fill='toself',
          name='Risk Profile',
          marker_color = 'rgba(211, 47, 47, 0.6)' # Red-ish with transparency
    ))

    fig_radar.update_layout(
      polar=dict(
        radialaxis=dict(
          visible=True,
          range=[0, 10] # Set the scale for your values
        )),
      showlegend=False,
      title='Key Risk Indicators',
      height=350, # Adjust height
      margin=dict(t=80, b=40, l=40, r=40) # Adjust margins
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# --- Row 4: Legend ---
st.markdown("---")
st.subheader("Legend")

leg1, leg2, leg3, leg4 = st.columns(4)

with leg1:
    st.markdown('<div class="legend-item"><div class="legend-color-box" style="background-color: #4CAF50;"></div> Approved</div>', unsafe_allow_html=True)
with leg2:
    st.markdown('<div class="legend-item"><div class="legend-color-box" style="background-color: #F44336;"></div> Declined</div>', unsafe_allow_html=True)
with leg3:
    st.markdown('<div class="legend-item"><div class="legend-color-box" style="background-color: #FFEB3B;"></div> Pending</div>', unsafe_allow_html=True)
with leg4:
    st.markdown('<div class="legend-item"><div class="legend-color-box" style="background-color: #9C27B0;"></div> Suspended</div>', unsafe_allow_html=True) # Purple for Suspended as per image

st.markdown("---")



