import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List

def create_kpi_cards(start_date_data: pd.DataFrame, lowest_cost_data: pd.DataFrame) -> Dict:
    """
    Create KPI cards comparing the two methods.
    
    Args:
        start_date_data (pd.DataFrame): Start date method results
        lowest_cost_data (pd.DataFrame): Lowest cost method results
        
    Returns:
        Dict: KPI metrics for display
    """
    # Calculate total metrics
    start_date_total_days = (start_date_data['Actual_End'].max() - 
                           start_date_data['Actual_Start'].min()).days
    lowest_cost_total_days = (lowest_cost_data['Actual_End'].max() - 
                            lowest_cost_data['Actual_Start'].min()).days
    
    start_date_total_cost = start_date_data['Segment_Cost'].sum()
    lowest_cost_total_cost = lowest_cost_data['Segment_Cost'].sum()
    
    # Get milestone metrics
    milestones = {}
    for milestone in [50, 75, 100]:
        # Get milestone days
        start_date_day = start_date_data[f'{milestone}%_Day'].iloc[0]
        lowest_cost_day = lowest_cost_data[f'{milestone}%_Day'].iloc[0]
        
        # Get milestone costs
        start_date_cost = start_date_data[f'{milestone}%_Cost'].iloc[0]
        lowest_cost_cost = lowest_cost_data[f'{milestone}%_Cost'].iloc[0]
        
        # Calculate differences
        if pd.notna(start_date_day) and pd.notna(lowest_cost_day):
            start_date_days = (start_date_day - start_date_data['Actual_Start'].min()).days
            lowest_cost_days = (lowest_cost_day - lowest_cost_data['Actual_Start'].min()).days
        else:
            start_date_days = None
            lowest_cost_days = None
        
        milestones[f'{milestone}%'] = {
            'start_date_days': start_date_days,
            'lowest_cost_days': lowest_cost_days,
            'start_date_cost': start_date_cost,
            'lowest_cost_cost': lowest_cost_cost
        }
    
    return {
        'total_days': {
            'start_date': start_date_total_days,
            'lowest_cost': lowest_cost_total_days,
            'difference': lowest_cost_total_days - start_date_total_days
        },
        'total_cost': {
            'start_date': start_date_total_cost,
            'lowest_cost': lowest_cost_total_cost,
            'difference': lowest_cost_total_cost - start_date_total_cost
        },
        'milestones': milestones
    }

def create_gantt_chart(data: pd.DataFrame, title: str) -> go.Figure:
    """
    Create a Gantt chart showing segment sequencing.
    
    Args:
        data (pd.DataFrame): Sequenced data with actual start/end dates
        title (str): Chart title
        
    Returns:
        go.Figure: Gantt chart
    """
    fig = go.Figure()
    
    # Add bars for each segment
    for idx, row in data.iterrows():
        fig.add_trace(go.Bar(
            name=row['Segment_Name'],
            x=[row['Duration']],
            y=[row['Segment_Name']],
            orientation='h',
            marker=dict(
                color=row['Segment_Cost'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Segment Cost ($)")
            ),
            hovertemplate=(
                f"<b>{row['Segment_Name']}</b><br>"
                f"Duration: {row['Duration']} days<br>"
                f"Miles: {row['Miles']:.1f}<br>"
                f"Cost: ${row['Segment_Cost']:,.0f}<br>"
                f"Start: {row['Actual_Start'].strftime('%Y-%m-%d')}<br>"
                f"End: {row['Actual_End'].strftime('%Y-%m-%d')}<br>"
                f"<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Duration (Days)",
        yaxis_title="Segment",
        height=400 + len(data) * 20,
        showlegend=False,
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig

def create_cumulative_progress_chart(start_date_data: pd.DataFrame, 
                                   lowest_cost_data: pd.DataFrame) -> go.Figure:
    """
    Create cumulative progress chart comparing both methods.
    
    Args:
        start_date_data (pd.DataFrame): Start date method results
        lowest_cost_data (pd.DataFrame): Lowest cost method results
        
    Returns:
        go.Figure: Cumulative progress chart
    """
    fig = go.Figure()
    
    # Create date range for x-axis
    all_dates = pd.concat([
        start_date_data[['Actual_Start', 'Actual_End']],
        lowest_cost_data[['Actual_Start', 'Actual_End']]
    ])
    min_date = all_dates.min().min()
    max_date = all_dates.max().max()
    
    # Generate daily data points for smooth curves
    date_range = pd.date_range(min_date, max_date, freq='D')
    
    # Calculate cumulative progress for start date method
    start_date_progress = []
    for date in date_range:
        completed = start_date_data[start_date_data['Actual_End'] <= date]
        if len(completed) > 0:
            progress = completed['Miles'].sum() / start_date_data['Miles'].sum() * 100
        else:
            progress = 0
        start_date_progress.append(progress)
    
    # Calculate cumulative progress for lowest cost method
    lowest_cost_progress = []
    for date in date_range:
        completed = lowest_cost_data[lowest_cost_data['Actual_End'] <= date]
        if len(completed) > 0:
            progress = completed['Miles'].sum() / lowest_cost_data['Miles'].sum() * 100
        else:
            progress = 0
        lowest_cost_progress.append(progress)
    
    # Add traces
    fig.add_trace(go.Scatter(
        x=date_range,
        y=start_date_progress,
        mode='lines',
        name='By Start Date',
        line=dict(color='blue', width=3),
        hovertemplate='<b>By Start Date</b><br>Date: %{x}<br>Progress: %{y:.1f}%<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=date_range,
        y=lowest_cost_progress,
        mode='lines',
        name='By Lowest Cost',
        line=dict(color='red', width=3),
        hovertemplate='<b>By Lowest Cost</b><br>Date: %{x}<br>Progress: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Cumulative Progress Comparison",
        xaxis_title="Date",
        yaxis_title="Progress (%)",
        height=500,
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_monthly_installation_chart(data: pd.DataFrame, title: str) -> go.Figure:
    """
    Create monthly installation chart with milestone markers.
    
    Args:
        data (pd.DataFrame): Sequenced data
        title (str): Chart title
        
    Returns:
        go.Figure: Monthly installation chart
    """
    # Group by month and segment
    data['Month'] = data['Actual_Start'].dt.to_period('M')
    monthly_data = data.groupby(['Month', 'Segment_Name']).agg({
        'Miles': 'sum',
        'Segment_Cost': 'sum'
    }).reset_index()
    
    # Convert period to datetime for plotting
    monthly_data['Month_Date'] = monthly_data['Month'].dt.to_timestamp()
    
    fig = go.Figure()
    
    # Add bars for each segment
    for segment in data['Segment_Name'].unique():
        segment_data = monthly_data[monthly_data['Segment_Name'] == segment]
        fig.add_trace(go.Bar(
            name=segment,
            x=segment_data['Month_Date'],
            y=segment_data['Miles'],
            hovertemplate=(
                f"<b>{segment}</b><br>"
                f"Month: %{{x|%B %Y}}<br>"
                f"Miles: %{{y:.1f}}<br>"
                f"<extra></extra>"
            )
        ))
    
    # Add milestone markers
    total_miles = data['Miles'].sum()
    for milestone in [0.5, 0.75, 1.0]:
        milestone_miles = total_miles * milestone
        milestone_date = data[data['Cumulative_Miles'] >= milestone_miles]['Actual_End'].iloc[0]
        if pd.notna(milestone_date):
            fig.add_vline(
                x=milestone_date,
                line_dash="dash",
                line_color="black",
                annotation_text=f"{int(milestone*100)}% Complete",
                annotation_position="top"
            )
    
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Miles Installed",
        barmode='stack',
        height=500,
        showlegend=True
    )
    
    return fig

def create_daily_production_chart(data: pd.DataFrame, title: str) -> go.Figure:
    """
    Create daily production rate trend chart.
    
    Args:
        data (pd.DataFrame): Sequenced data
        title (str): Chart title
        
    Returns:
        go.Figure: Daily production chart
    """
    # Calculate daily production rates
    daily_production = []
    dates = []
    
    for _, row in data.iterrows():
        # Calculate daily rate for this segment
        daily_rate = row['Miles'] / row['Duration']
        
        # Add data points for each day of the segment
        for day in range(row['Duration']):
            date = row['Actual_Start'] + timedelta(days=day)
            dates.append(date)
            daily_production.append(daily_rate)
    
    # Create DataFrame for plotting
    production_df = pd.DataFrame({
        'Date': dates,
        'Daily_Production': daily_production
    })
    
    # Group by date and sum production rates
    daily_summary = production_df.groupby('Date')['Daily_Production'].sum().reset_index()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=daily_summary['Date'],
        y=daily_summary['Daily_Production'],
        mode='lines+markers',
        name='Daily Production',
        line=dict(color='green', width=2),
        hovertemplate='<b>Daily Production</b><br>Date: %{x}<br>Rate: %{y:.2f} miles/day<extra></extra>'
    ))
    
    # Add moving average
    window = min(7, len(daily_summary))
    if window > 1:
        moving_avg = daily_summary['Daily_Production'].rolling(window=window, center=True).mean()
        fig.add_trace(go.Scatter(
            x=daily_summary['Date'],
            y=moving_avg,
            mode='lines',
            name=f'{window}-Day Moving Average',
            line=dict(color='orange', width=2, dash='dash'),
            hovertemplate='<b>Moving Average</b><br>Date: %{x}<br>Rate: %{y:.2f} miles/day<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Production Rate (miles/day)",
        height=400,
        hovermode='x unified'
    )
    
    return fig

def create_cost_efficiency_chart(start_date_data: pd.DataFrame, 
                               lowest_cost_data: pd.DataFrame) -> go.Figure:
    """
    Create cost efficiency comparison chart.
    
    Args:
        start_date_data (pd.DataFrame): Start date method results
        lowest_cost_data (pd.DataFrame): Lowest cost method results
        
    Returns:
        go.Figure: Cost efficiency chart
    """
    fig = go.Figure()
    
    # Calculate cumulative cost efficiency over time
    methods = {
        'By Start Date': start_date_data,
        'By Lowest Cost': lowest_cost_data
    }
    
    colors = {'By Start Date': 'blue', 'By Lowest Cost': 'red'}
    
    for method_name, data in methods.items():
        # Calculate efficiency (miles per dollar)
        data['Efficiency'] = data['Cumulative_Miles'] / data['Cumulative_Cost']
        
        fig.add_trace(go.Scatter(
            x=data['Actual_End'],
            y=data['Efficiency'],
            mode='lines+markers',
            name=method_name,
            line=dict(color=colors[method_name], width=3),
            hovertemplate=(
                f"<b>{method_name}</b><br>"
                f"Date: %{{x}}<br>"
                f"Efficiency: %{{y:.4f}} miles/$<br>"
                f"<extra></extra>"
            )
        ))
    
    fig.update_layout(
        title="Cost Efficiency Over Time",
        xaxis_title="Date",
        yaxis_title="Efficiency (miles per dollar)",
        height=400,
        hovermode='x unified'
    )
    
    return fig 