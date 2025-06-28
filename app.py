import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Import our custom modules
from data_generator import load_sample_data
from sequencing_logic import FiberSequencer
from visualizations import create_kpi_cards, create_cumulative_progress_chart

# Page configuration
st.set_page_config(
    page_title="Fiber Sequencing Comparison",
    page_icon="📊",
    layout="wide"
)

def main():
    st.title("Fiber Construction Sequencing Comparison")
    st.markdown("Compare Start Date vs. Lowest Cost sequencing methods")
    
    # Simple sidebar
    with st.sidebar:
        st.header("Settings")
        
        # Data source
        use_sample = st.checkbox("Use Sample Data", value=True)
        
        if not use_sample:
            uploaded_file = st.file_uploader("Upload CSV/Excel file", type=['csv', 'xlsx'])
            if uploaded_file is None:
                st.stop()
            
            try:
                if uploaded_file.name.endswith('.csv'):
                    data = pd.read_csv(uploaded_file)
                else:
                    data = pd.read_excel(uploaded_file)
                
                if 'Start_Date' in data.columns:
                    data['Start_Date'] = pd.to_datetime(data['Start_Date'])
                
                st.success(f"Loaded {len(data)} segments")
            except Exception as e:
                st.error(f"Error loading file: {e}")
                st.stop()
        else:
            data = load_sample_data()
            st.success(f"Using {len(data)} sample segments")
        
        # Simple parameters
        st.subheader("Parameters")
        start_offset = st.slider("Start Date Offset (days)", -30, 30, 0)
        prod_mult = st.slider("Production Multiplier", 0.5, 2.0, 1.0, 0.1)
    
    # Main content
    if 'data' in locals():
        # Initialize sequencer
        sequencer = FiberSequencer(data)
        sequencer.apply_parameters(
            start_date_offset=start_offset,
            production_multiplier=prod_mult
        )
        
        # Calculate sequences
        start_date_method = sequencer.sequence_by_start_date()
        lowest_cost_method = sequencer.sequence_by_lowest_cost()
        
        # Get metrics
        kpi_metrics = create_kpi_cards(start_date_method, lowest_cost_method)
        
        # Simple comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Start Date")
            st.metric("Total Days", kpi_metrics['total_days']['start_date'])
            st.metric("Total Cost", f"${kpi_metrics['total_cost']['start_date']:,.0f}")
        
        with col2:
            st.subheader("By Lowest Cost")
            st.metric("Total Days", kpi_metrics['total_days']['lowest_cost'])
            st.metric("Total Cost", f"${kpi_metrics['total_cost']['lowest_cost']:,.0f}")
        
        # Key differences
        st.subheader("Key Differences")
        day_diff = kpi_metrics['total_days']['difference']
        cost_diff = kpi_metrics['total_cost']['difference']
        
        if day_diff > 0:
            st.info(f"Lowest Cost method takes {day_diff} more days")
        else:
            st.info(f"Lowest Cost method saves {abs(day_diff)} days")
        
        if cost_diff > 0:
            st.warning(f"Lowest Cost method costs ${cost_diff:,.0f} more")
        else:
            st.success(f"Lowest Cost method saves ${abs(cost_diff):,.0f}")
        
        # Progress chart
        st.subheader("Progress Comparison")
        progress_fig = create_cumulative_progress_chart(start_date_method, lowest_cost_method)
        st.plotly_chart(progress_fig, use_container_width=True)
        
        # Simple pros/cons
        st.subheader("Summary")
        
        analysis = sequencer.get_pros_cons_analysis(start_date_method, lowest_cost_method)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Start Date Method:**")
            st.write("✅ Easier scheduling")
            st.write("✅ Natural timeline")
            st.write("❌ May cost more")
        
        with col2:
            st.write("**Lowest Cost Method:**")
            st.write("✅ Cost efficient")
            st.write("✅ Better budget control")
            st.write("❌ Complex scheduling")

if __name__ == "__main__":
    main() 