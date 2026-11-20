import pandas as pd
from datetime import datetime

# Columns the loader expects, in order
OUTPUT_COLUMNS = [
    'user_id', 'source_id', 'external_id', 'activity_type', 'activity_name',
    'start_time', 'duration_seconds', 'distance_meters', 'calories_burned',
    'average_heart_rate', 'max_heart_rate', 'elevation_gain_meters',
    'created_at', 'updated_at'
]


def _column(df, name, default):
    """Return a column from the DataFrame, or a column of the default value if Strava did not send it"""
    if name in df.columns:
        return df[name]
    return pd.Series([default] * len(df), index=df.index)


class StravaTransformer:
    def __init__(self):
        pass

    def transform_activities(self, df, source_id, user_id=1):
        """Transform Strava API data to match our database schema.

        source_id: ID of the 'strava' data source (use DatabaseLoader.get_source_id('strava'))
        user_id: ID of the user (use DatabaseLoader.get_or_create_user())
        """

        # No activities came back from Strava
        if df is None or len(df) == 0:
            return pd.DataFrame(columns=OUTPUT_COLUMNS)

        transformed_df = pd.DataFrame()

        transformed_df['user_id'] = pd.Series([user_id] * len(df), dtype='int64')
        transformed_df['source_id'] = pd.Series([source_id] * len(df), dtype='int64')
        transformed_df['external_id'] = df['id'].astype(str).values  # Strava's unique activity ID
        transformed_df['activity_type'] = _column(df, 'type', 'Unknown').values
        transformed_df['activity_name'] = _column(df, 'name', 'Strava Activity').values

        # Strava sends UTC times. Store them without the timezone, as the database column expects
        transformed_df['start_time'] = pd.to_datetime(df['start_date']).dt.tz_localize(None).values

        transformed_df['duration_seconds'] = _column(df, 'moving_time', 0).fillna(0).astype('int64').values
        transformed_df['distance_meters'] = _column(df, 'distance', 0.0).fillna(0).astype('float64').values

        # The Strava activity list does not include calories, so they are filled with 0
        transformed_df['calories_burned'] = pd.to_numeric(_column(df, 'calories', 0)).fillna(0).astype('int64').values

        # Heart rate fields (not all activities have these, so missing stays empty)
        transformed_df['average_heart_rate'] = pd.to_numeric(_column(df, 'average_heartrate', pd.NA)).round().astype('Int64').values
        transformed_df['max_heart_rate'] = pd.to_numeric(_column(df, 'max_heartrate', pd.NA)).round().astype('Int64').values

        # Elevation gain
        transformed_df['elevation_gain_meters'] = pd.to_numeric(_column(df, 'total_elevation_gain', 0.0)).fillna(0).astype('float64').values

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
    # source_id=1 is a placeholder for this demo only (nothing is saved to the database)
    transformed = transformer.transform_activities(raw_data, source_id=1)

    print("Transformed Strava data:")
    print(transformed[['activity_type', 'activity_name', 'start_time', 'duration_seconds', 'distance_meters']].head())
