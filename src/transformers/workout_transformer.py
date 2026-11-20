import pandas as pd
from datetime import datetime
import sys
import os


class WorkoutTransformer:
    def __init__(self):
        pass

    def transform_csv_workouts(self, df, source_id, user_id=1):
        """Transform CSV workout data to match our database schema.

        source_id: ID of the 'manual' data source (use DatabaseLoader.get_source_id('manual'))
        user_id: ID of the user (use DatabaseLoader.get_or_create_user())
        """

        # Optional columns: add them as empty if the CSV does not have them
        df = df.copy()
        for col in ['distance_km', 'calories', 'heart_rate_avg', 'elevation_gain_m']:
            if col not in df.columns:
                df[col] = pd.NA

        # Create transformed dataframe with explicit data types
        transformed_df = pd.DataFrame()

        # Map columns to our schema
        transformed_df['user_id'] = pd.Series([user_id] * len(df), dtype='int64')
        transformed_df['source_id'] = pd.Series([source_id] * len(df), dtype='int64')

        # Stable ID built from the row content, so loading a different CSV
        # (or the same one twice) never mixes up rows
        transformed_df['external_id'] = (
            df['date'].dt.strftime('%Y-%m-%d') + '_' +
            df['activity_type'].astype(str) + '_' +
            df['duration_minutes'].astype(str) + '_' +
            df['distance_km'].astype(str)
        ).values

        transformed_df['activity_type'] = df['activity_type'].values
        transformed_df['activity_name'] = df['activity_type'].apply(lambda x: f"{str(x).title()} Workout").values
        transformed_df['start_time'] = df['date'].values
        transformed_df['duration_seconds'] = (df['duration_minutes'] * 60).round().astype('int64').values

        # Handle distance (convert km to meters)
        transformed_df['distance_meters'] = (pd.to_numeric(df['distance_km']).fillna(0) * 1000).astype('float64').values

        # Handle calories
        transformed_df['calories_burned'] = pd.to_numeric(df['calories']).fillna(0).astype('int64').values

        # Heart rate: keep missing values empty instead of 0
        transformed_df['average_heart_rate'] = pd.to_numeric(df['heart_rate_avg']).round().astype('Int64').values
        transformed_df['max_heart_rate'] = pd.Series([pd.NA] * len(df), dtype='Int64')

        # Handle elevation gain
        transformed_df['elevation_gain_meters'] = pd.to_numeric(df['elevation_gain_m']).fillna(0).astype('float64').values

        transformed_df['created_at'] = datetime.now()
        transformed_df['updated_at'] = datetime.now()

        return transformed_df


if __name__ == "__main__":
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from extractors.csv_extractor import CSVExtractor

    extractor = CSVExtractor('data/sample_workouts.csv')
    raw_data = extractor.extract_workouts()

    transformer = WorkoutTransformer()
    # source_id=1 is a placeholder for this demo only (nothing is saved to the database)
    transformed_data = transformer.transform_csv_workouts(raw_data, source_id=1)

    print("Transformed data:")
    print(transformed_data.head())
    print("\nData types:")
    print(transformed_data.dtypes)
