#!/usr/bin/env python3
"""
Test script to verify all modules work correctly.
"""

import pandas as pd
from data_generator import generate_sample_data
from sequencing_logic import FiberSequencer
from visualizations import create_kpi_cards, create_gantt_chart

def test_modules():
    """Test all modules to ensure they work correctly."""
    print("🧪 Testing Fiber Construction Sequencing Modules...")
    
    # Test 1: Data Generation
    print("\n1. Testing Data Generation...")
    try:
        data = generate_sample_data(num_segments=10)
        print(f"✅ Generated {len(data)} sample segments")
        print(f"   Total miles: {data['Miles'].sum():.1f}")
        print(f"   Total cost: ${data['Segment_Cost'].sum():,.0f}")
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False
    
    # Test 2: Sequencing Logic
    print("\n2. Testing Sequencing Logic...")
    try:
        sequencer = FiberSequencer(data)
        
        # Test start date sequencing
        start_date_method = sequencer.sequence_by_start_date()
        print(f"✅ Start date sequencing: {len(start_date_method)} segments")
        
        # Test lowest cost sequencing
        lowest_cost_method = sequencer.sequence_by_lowest_cost()
        print(f"✅ Lowest cost sequencing: {len(lowest_cost_method)} segments")
        
        # Test parameters
        sequencer.apply_parameters(start_date_offset=5, production_multiplier=1.2)
        print("✅ Parameter application successful")
        
    except Exception as e:
        print(f"❌ Sequencing logic failed: {e}")
        return False
    
    # Test 3: Visualizations
    print("\n3. Testing Visualizations...")
    try:
        # Test KPI cards
        kpi_metrics = create_kpi_cards(start_date_method, lowest_cost_method)
        print(f"✅ KPI metrics calculated")
        print(f"   Start date total days: {kpi_metrics['total_days']['start_date']}")
        print(f"   Lowest cost total days: {kpi_metrics['total_days']['lowest_cost']}")
        
        # Test Gantt chart
        gantt_fig = create_gantt_chart(start_date_method, "Test Gantt Chart")
        print("✅ Gantt chart created successfully")
        
    except Exception as e:
        print(f"❌ Visualizations failed: {e}")
        return False
    
    # Test 4: Pros & Cons Analysis
    print("\n4. Testing Pros & Cons Analysis...")
    try:
        analysis = sequencer.get_pros_cons_analysis(start_date_method, lowest_cost_method)
        print("✅ Pros & cons analysis generated")
        print(f"   Start date pros: {len(analysis['By Start Date']['pros'])}")
        print(f"   Lowest cost pros: {len(analysis['By Lowest Cost First']['pros'])}")
        
    except Exception as e:
        print(f"❌ Pros & cons analysis failed: {e}")
        return False
    
    print("\n🎉 All tests passed! The application is ready to run.")
    return True

if __name__ == "__main__":
    success = test_modules()
    if success:
        print("\n🚀 You can now run the Streamlit app with:")
        print("   streamlit run app.py")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 