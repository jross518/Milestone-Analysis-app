import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple

class FiberSequencer:
    """Handles fiber construction sequencing logic for different methods."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize sequencer with segment data.
        
        Args:
            data (pd.DataFrame): DataFrame with segment information
        """
        self.original_data = data.copy()
        self.data = data.copy()
        
    def apply_parameters(self, start_date_offset: int = 0, 
                        production_multiplier: float = 1.0,
                        cost_threshold: float = None):
        """
        Apply what-if scenario parameters to the data.
        
        Args:
            start_date_offset (int): Days to offset all start dates
            production_multiplier (float): Multiplier for production rates
            cost_threshold (float): Optional cost filter threshold
        """
        self.data = self.original_data.copy()
        
        # Apply start date offset
        if start_date_offset != 0:
            self.data['Start_Date'] = self.data['Start_Date'] + timedelta(days=start_date_offset)
        
        # Apply production rate multiplier
        if production_multiplier != 1.0:
            self.data['EstRate'] = self.data['EstRate'] * production_multiplier
            # Recalculate duration based on new production rate
            self.data['Duration'] = np.ceil(self.data['Miles'] / self.data['EstRate']).astype(int)
        
        # Apply cost threshold filter
        if cost_threshold is not None:
            self.data = self.data[self.data['Segment_Cost'] <= cost_threshold].copy()
    
    def sequence_by_start_date(self) -> pd.DataFrame:
        """
        Sequence segments by their start date (CSD/BD method).
        
        Returns:
            pd.DataFrame: Sequenced data with calculated schedule
        """
        sequenced = self.data.sort_values('Start_Date').copy()
        return self._calculate_schedule(sequenced)
    
    def sequence_by_lowest_cost(self) -> pd.DataFrame:
        """
        Sequence segments by lowest cost first.
        
        Returns:
            pd.DataFrame: Sequenced data with calculated schedule
        """
        sequenced = self.data.sort_values('Segment_Cost').copy()
        return self._calculate_schedule(sequenced)
    
    def _calculate_schedule(self, sequenced_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate the actual schedule for sequenced segments.
        
        Args:
            sequenced_data (pd.DataFrame): Data sorted by sequencing method
            
        Returns:
            pd.DataFrame: Data with calculated start/end dates and progress
        """
        result = sequenced_data.copy()
        
        # Calculate actual start and end dates
        current_date = result['Start_Date'].min()
        actual_start_dates = []
        actual_end_dates = []
        
        for _, row in result.iterrows():
            # Use the later of planned start date or current date
            actual_start = max(row['Start_Date'], current_date)
            actual_start_dates.append(actual_start)
            
            # Calculate end date based on duration
            end_date = actual_start + timedelta(days=row['Duration'])
            actual_end_dates.append(end_date)
            
            # Update current date for next segment
            current_date = end_date
        
        result['Actual_Start'] = actual_start_dates
        result['Actual_End'] = actual_end_dates
        
        # Calculate cumulative metrics
        result = self._calculate_cumulative_metrics(result)
        
        return result
    
    def _calculate_cumulative_metrics(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate cumulative miles, costs, and progress over time.
        
        Args:
            data (pd.DataFrame): Data with actual start/end dates
            
        Returns:
            pd.DataFrame: Data with cumulative metrics
        """
        result = data.copy()
        
        # Sort by actual start date for cumulative calculations
        result = result.sort_values('Actual_Start').reset_index(drop=True)
        
        # Calculate cumulative metrics
        result['Cumulative_Miles'] = result['Miles'].cumsum()
        result['Cumulative_Cost'] = result['Segment_Cost'].cumsum()
        result['Cumulative_Percent'] = (result['Cumulative_Miles'] / result['Miles'].sum() * 100).round(1)
        
        # Calculate milestone achievements
        total_miles = result['Miles'].sum()
        milestones = [0.5, 0.75, 1.0]  # 50%, 75%, 100%
        
        for milestone in milestones:
            milestone_miles = total_miles * milestone
            milestone_idx = (result['Cumulative_Miles'] >= milestone_miles).idxmax()
            
            if milestone_idx < len(result):
                milestone_row = result.iloc[milestone_idx]
                result[f'{int(milestone*100)}%_Day'] = milestone_row['Actual_End']
                result[f'{int(milestone*100)}%_Cost'] = milestone_row['Cumulative_Cost']
            else:
                result[f'{int(milestone*100)}%_Day'] = None
                result[f'{int(milestone*100)}%_Cost'] = None
        
        return result
    
    def get_milestone_comparison(self, start_date_method: pd.DataFrame, 
                               lowest_cost_method: pd.DataFrame) -> Dict:
        """
        Compare milestone achievements between the two methods.
        
        Args:
            start_date_method (pd.DataFrame): Results from start date sequencing
            lowest_cost_method (pd.DataFrame): Results from lowest cost sequencing
            
        Returns:
            Dict: Comparison metrics
        """
        comparison = {}
        
        for milestone in [50, 75, 100]:
            # Get milestone days
            start_date_day = start_date_method[f'{milestone}%_Day'].iloc[0]
            lowest_cost_day = lowest_cost_method[f'{milestone}%_Day'].iloc[0]
            
            # Get milestone costs
            start_date_cost = start_date_method[f'{milestone}%_Cost'].iloc[0]
            lowest_cost_cost = lowest_cost_method[f'{milestone}%_Cost'].iloc[0]
            
            # Calculate differences
            if start_date_day and lowest_cost_day:
                day_diff = (lowest_cost_day - start_date_day).days
            else:
                day_diff = None
            
            if start_date_cost and lowest_cost_cost:
                cost_diff = lowest_cost_cost - start_date_cost
            else:
                cost_diff = None
            
            comparison[f'{milestone}%'] = {
                'start_date_day': start_date_day,
                'lowest_cost_day': lowest_cost_day,
                'day_diff': day_diff,
                'start_date_cost': start_date_cost,
                'lowest_cost_cost': lowest_cost_cost,
                'cost_diff': cost_diff
            }
        
        return comparison
    
    def get_pros_cons_analysis(self, start_date_method: pd.DataFrame, 
                              lowest_cost_method: pd.DataFrame) -> Dict:
        """
        Generate pros and cons analysis for each method.
        
        Args:
            start_date_method (pd.DataFrame): Results from start date sequencing
            lowest_cost_method (pd.DataFrame): Results from lowest cost sequencing
            
        Returns:
            Dict: Pros and cons analysis
        """
        # Calculate key metrics
        start_date_total_days = (start_date_method['Actual_End'].max() - 
                               start_date_method['Actual_Start'].min()).days
        lowest_cost_total_days = (lowest_cost_method['Actual_End'].max() - 
                                lowest_cost_method['Actual_Start'].min()).days
        
        start_date_total_cost = start_date_method['Segment_Cost'].sum()
        lowest_cost_total_cost = lowest_cost_method['Segment_Cost'].sum()
        
        # Calculate early efficiency (first 25% of segments)
        start_date_early = start_date_method.head(len(start_date_method)//4)
        lowest_cost_early = lowest_cost_method.head(len(lowest_cost_method)//4)
        
        start_date_early_efficiency = start_date_early['Miles'].sum() / start_date_early['Segment_Cost'].sum()
        lowest_cost_early_efficiency = lowest_cost_early['Miles'].sum() / lowest_cost_early['Segment_Cost'].sum()
        
        analysis = {
            'By Start Date': {
                'pros': [
                    'Follows natural project timeline',
                    'Minimizes schedule conflicts',
                    'Easier resource planning',
                    'Reduces coordination complexity'
                ],
                'cons': [
                    f'May take {start_date_total_days} days to complete',
                    'Higher early costs due to expensive early segments',
                    'Less cost optimization',
                    'Potential for cost overruns'
                ],
                'metrics': {
                    'total_days': start_date_total_days,
                    'total_cost': start_date_total_cost,
                    'early_efficiency': start_date_early_efficiency
                }
            },
            'By Lowest Cost First': {
                'pros': [
                    f'Lower total cost: ${lowest_cost_total_cost:,.0f}',
                    'Better cost efficiency',
                    'Faster early progress',
                    'More predictable budget'
                ],
                'cons': [
                    f'May take {lowest_cost_total_days} days to complete',
                    'Complex resource scheduling',
                    'Potential for delays due to coordination',
                    'Risk of schedule conflicts'
                ],
                'metrics': {
                    'total_days': lowest_cost_total_days,
                    'total_cost': lowest_cost_total_cost,
                    'early_efficiency': lowest_cost_early_efficiency
                }
            }
        }
        
        return analysis 