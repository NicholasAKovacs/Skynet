import pandas as pd
import numpy as np

def calculate_recovery_rate(df: pd.DataFrame, 
                            date_col: str = 'Date', 
                            value_col: str = 'Passengers', 
                            baseline_year: int = 2019) -> pd.DataFrame:
    """
    Calculates the recovery rate of a value column relative to a baseline year,
    matched by Month.
    
    Args:
        df: Input DataFrame containing time series data.
        date_col: Name of the date column.
        value_col: Name of the value column (e.g., 'Passengers').
        baseline_year: The year to use as the 100% baseline (default 2019).
        
    Returns:
        DataFrame with an added 'recovery_rate' column.
    """
    # Ensure datetime
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    
    # Extract month and year
    df['Month'] = df[date_col].dt.month
    df['Year'] = df[date_col].dt.year
    
    # Create baseline lookup
    baseline_data = df[df['Year'] == baseline_year].set_index('Month')[value_col]
    
    if baseline_data.empty:
        raise ValueError(f"No data found for baseline year {baseline_year}")
        
    # Function to apply recovery calculation
    def get_baseline(row):
        return baseline_data.get(row['Month'], np.nan)
        
    df['baseline_value'] = df.apply(get_baseline, axis=1)
    df['recovery_rate'] = df[value_col] / df['baseline_value']
    
    return df

def detect_recovery_milestones(df: pd.DataFrame, 
                               threshold: float = 1.0) -> dict:
    """
    Identifies the first date where recovery rate exceeds a threshold.
    """
    recovered = df[df['recovery_rate'] >= threshold].sort_values('Date')
    if not recovered.empty:
        return {
            'recovered': True,
            'date': recovered.iloc[0]['Date'],
            'value': recovered.iloc[0]['recovery_rate']
        }
    else:
        return {'recovered': False, 'date': None, 'value': None}
