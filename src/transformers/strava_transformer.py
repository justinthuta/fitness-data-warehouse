import pandas as pd
from datetime import datetime

class StravaTransformer:
    def __init__(self):
        pass
    
    def transform_activities(self, df, user_id=1, source_id=1):  # source_id=1 for 'strava'
        """Transform Strava API data to match our database schema"""
        
        transformed_df = pd.DataFrame()
        
        transformed_df['user_id'] = pd.Series([user_id] * len(df), dtype='int64')
        transformed_df['source_id'] = pd.Series([source_id] * len(df), dtype='int64')
        transformed_df['external_id'] = df['id'].astype(str)  # Strava's unique activity ID
        transformed_df['activity_type'] = df['type']
        transformed_df['activity_name'] = df['name']
        transformed_df['start_time'] = pd.to_datetime(df['start_date'])
        transformed_df['duration_seconds'] = df['moving_time'].astype('int64')
        transformed_df['distance_meters'] = df['distance'].astype('float64')
        
        # Strava provides calories only sometimes - fill missing with 0
        transformed_df['calories_burned'] = df.get('calories', 0)
        transformed_df['calories_burned'] = transformed_df['calories_burned'].fillna(0).astype('int64')
        
        # Heart rate fields (not all activities have these)
        transformed_df['average_heart_rate'] = df.get('average_heartrate', None)
        transformed_df['max_heart_rate'] = df.get('max_heartrate', None)
        
        # Elevation gain
        transformed_df['elevation_gain_meters'] = df.get('total_elevation_gain', 0).astype('float64')
        
        transformed_df['created_at'] = datetime.now()
        transformed_df['updated_at'] = datetime.now()
        
        return transformed_df

if __name__ == "__main__":
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from extractors.strava_extractor import StravaExtractor
    
    extractor = StravaExtractor()
    raw_data = extractor.extract_activities()
    
    transformer = StravaTransformer()
    transformed = transformer.transform_activities(raw_data)
    
    print("Transformed Strava data:")
    print(transformed[['activity_type', 'activity_name', 'start_time', 'duration_seconds', 'distance_meters']].head())
