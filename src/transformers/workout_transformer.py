import pandas as pd
from datetime import datetime
import sys
import os

class WorkoutTransformer:
    def __init__(self):
        pass
    
    def transform_csv_workouts(self, df, user_id=1, source_id=5):  # source_id=5 for 'manual'
        """Transform CSV workout data to match our database schema"""
        
        # Create transformed dataframe with explicit data types
        transformed_df = pd.DataFrame()
        
        # Map columns to our schema
        transformed_df['user_id'] = pd.Series([user_id] * len(df), dtype='int64')
        transformed_df['source_id'] = pd.Series([source_id] * len(df), dtype='int64')
        transformed_df['external_id'] = df.index.astype(str)
        transformed_df['activity_type'] = df['activity_type']
        transformed_df['activity_name'] = df['activity_type'].apply(lambda x: f"{x.title()} Workout")
        transformed_df['start_time'] = df['date']
        transformed_df['duration_seconds'] = (df['duration_minutes'] * 60).astype('int64')
        
        # Handle distance (convert km to meters)
        transformed_df['distance_meters'] = (df['distance_km'].fillna(0) * 1000).astype('float64')
        
        # Handle calories
        transformed_df['calories_burned'] = df['calories'].fillna(0).astype('int64')
        
        # Handle heart rate
        transformed_df['average_heart_rate'] = df['heart_rate_avg'].fillna(0).astype('int64')
        
        # Handle elevation gain
        transformed_df['elevation_gain_meters'] = df['elevation_gain_m'].fillna(0).astype('float64')
        
        transformed_df['max_heart_rate'] = None
        transformed_df['created_at'] = datetime.now()
        transformed_df['updated_at'] = datetime.now()
        
        return transformed_df

if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from extractors.csv_extractor import CSVExtractor
    
    extractor = CSVExtractor('data/sample_workouts.csv')
    raw_data = extractor.extract_workouts()
    
    transformer = WorkoutTransformer()
    transformed_data = transformer.transform_csv_workouts(raw_data)
    
    print("Transformed data:")
    print(transformed_data.head())
    print(f"\nData types:")
    print(transformed_data.dtypes)
