import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_sample_data(num_segments=29, base_date= None):
    """
    Generate realistic sample data for fiber construction segments.
    
    Args:
        num_segments (int): Number of segments to generate
        base_date (datetime): Base date for start dates, defaults to today
    
    Returns:
        pd.DataFrame: Sample data with required columns
    """
    if base_date is None:
        base_date = datetime.now()
    
    # Set random seed for reproducibility
    np.random.seed(42)
    random.seed(42)
    
    # Generate segment names
    segment_names = [f"Segment_{i:02d}" for i in range(1, num_segments + 1)]
    
    # Generate realistic parameters
    miles = np.random.uniform(0.05, 50, num_segments).round(1)
    cost_per_mile = np.random.uniform(8000, 25000, num_segments).round(0)
    segment_cost = (miles * cost_per_mile).round(0)
    
    # Generate start dates (spread over 6 months)
    start_dates = []
    for i in range(num_segments):
        days_offset = np.random.randint(0, 180)
        start_date = base_date + timedelta(days=days_offset)
        start_dates.append(start_date)
    
    # Generate durations (5-30 days)
    durations = np.random.randint(5, 31, num_segments)
    
    # Generate production rates (0.5-3.0 miles per day)
    production_rates = np.random.uniform(0.5, 3.0, num_segments).round(1)
    
    # Create DataFrame
    data = pd.DataFrame({
        'Segment_Name': segment_names,
        'Start_Date': start_dates,
        'Duration': durations,
        'EstRate': production_rates,
        'Cost_Per_Mile': cost_per_mile,
        'Segment_Cost': segment_cost,
        'Miles': miles
    })
    
    # Sort by start date for realistic sequencing
    data = data.sort_values('Start_Date').reset_index(drop=True)
    
    return data

def save_sample_data(data, filename='sample_fiber_data.csv'):
    """Save sample data to CSV file."""
    data.to_csv(filename, index=False)
    return filename

def load_sample_data():
    """Load or generate sample data."""
    try:
        data = pd.read_csv('sample_fiber_data.csv')
        data['Start_Date'] = pd.to_datetime(data['Start_Date'])
        return data
    except FileNotFoundError:
        data = generate_sample_data()
        save_sample_data(data)
        return data

if __name__ == "__main__":
    # Generate and save sample data
    data = generate_sample_data()
    save_sample_data(data)
    print("Sample data generated and saved to 'sample_fiber_data.csv'")
    print(f"Generated {len(data)} segments")
    print("\nFirst few rows:")
    print(data.head()) 