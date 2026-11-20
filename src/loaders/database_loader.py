import pandas as pd
import sys
import os
import logging
from sqlalchemy import text

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.connection import DatabaseConnection

DEFAULT_USERNAME = 'default_user'


class DatabaseLoader:
    def __init__(self):
        self.db = DatabaseConnection()
        self.logger = self._setup_logger()

    def _setup_logger(self):
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/loader.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)

    def get_source_id(self, source_name):
        """Look up a data source ID by name (for example 'strava' or 'manual')"""
        engine = self.db.get_engine()
        with engine.connect() as conn:
            row = conn.execute(
                text("SELECT source_id FROM data_sources WHERE source_name = :name"),
                {"name": source_name}
            ).fetchone()
        if row is None:
            raise ValueError(
                f"Data source '{source_name}' not found. "
                "Run: python3 src/database/connection.py to create the tables and seed data."
            )
        return int(row[0])

    def get_or_create_user(self, username=DEFAULT_USERNAME):
        """Return the user ID for this username, creating the user if needed.
        Activities have a foreign key to users, so a user must exist before loading."""
        engine = self.db.get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO users (username) VALUES (:username) "
                     "ON CONFLICT (username) DO NOTHING"),
                {"username": username}
            )
            row = conn.execute(
                text("SELECT user_id FROM users WHERE username = :username"),
                {"username": username}
            ).fetchone()
        return int(row[0])

    def load_activities(self, df):
        """Load activities data into the database"""
        if df is None or len(df) == 0:
            self.logger.info("Nothing to load")
            return True

        try:
            engine = self.db.get_engine()

            df.to_sql(
                'activities',
                engine,
                if_exists='append',
                index=False,
                method='multi'
            )

            self.logger.info(f"Loaded {len(df)} activities to database")
            return True

        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return False

    def check_duplicates(self, df):
        """Remove activities that are already stored (same source and external ID),
        and duplicates inside the new data itself"""
        if df is None or len(df) == 0:
            return df

        # Duplicates inside the new data
        df = df.drop_duplicates(subset=['source_id', 'external_id'])

        try:
            engine = self.db.get_engine()
            new_records = df

            # One source at a time (usually just one)
            for source_id in df['source_id'].unique():
                existing_ids = pd.read_sql(
                    text("SELECT external_id FROM activities WHERE source_id = :source_id"),
                    engine,
                    params={"source_id": int(source_id)}
                )['external_id'].tolist()

                is_dup = (new_records['source_id'] == source_id) & new_records['external_id'].isin(existing_ids)
                new_records = new_records[~is_dup]

            if len(new_records) < len(df):
                self.logger.info(f"Filtered out {len(df) - len(new_records)} duplicate records")

            return new_records
        except Exception as e:
            # Do not guess: if we cannot check, stop instead of risking duplicate rows
            self.logger.error(f"Error checking duplicates: {e}")
            raise


if __name__ == "__main__":
    # Run the sample CSV through the full ETL pipeline
    from extractors.csv_extractor import CSVExtractor
    from transformers.workout_transformer import WorkoutTransformer

    loader = DatabaseLoader()
    user_id = loader.get_or_create_user()
    source_id = loader.get_source_id('manual')

    # Extract and transform data
    extractor = CSVExtractor('data/sample_workouts.csv')
    raw_data = extractor.extract_workouts()

    transformer = WorkoutTransformer()
    transformed_data = transformer.transform_csv_workouts(raw_data, user_id=user_id, source_id=source_id)

    # Load data
    clean_data = loader.check_duplicates(transformed_data)

    print(f"Records to load: {len(clean_data)}")
    success = loader.load_activities(clean_data)

    if success:
        print("Data loaded successfully!")
    else:
        print("Failed to load data")
