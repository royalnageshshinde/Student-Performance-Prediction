import re
import pandas as pd

def time_to_minutes(time_str):
    try:
        if pd.isna(time_str) or time_str in ['', ' ', '-']:
            return 0
            
        if isinstance(time_str, (int, float)):
            return int(time_str)
            
        # Handle all time formats (7hrs 36min, 2hrs, 45min, etc.)
        time_str = str(time_str).lower().replace('