import pandas as pd
import sys
import os
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database.connection import DatabaseConnection

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
    
    def load_activities(self, df):
        """Load activities data into the database"""
        try:
            engine = self.db.get_engine()
            
            # Use pandas to_sql to load data
            rows_inserted = df.to_sql(
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
        """Check for duplicates before loading"""
        try:
            engine = self.db.get_engine()
            
            # Get existing external_ids for this source
            existing_ids = pd.read_sql(
                f"SELECT external_id FROM activities WHERE source_id = {df['source_id'].iloc[0]}",
                engine
            )['external_id'].tolist()
            
            # Filter out duplicates
            new_records = df[~df['external_id'].isin(existing_ids)]
            
            if len(new_records) < len(df):
                self.logger.info(f"Filtered out {len(df) - len(new_records)} duplicate records")
            
            return new_records
        except Exception as e:
            self.logger.error(f"Error checking duplicates: {e}")
            return df

if __name__ == "__main__":
    # Test the loader with sample data
    from extractors.csv_extractor import CSVExtractor
    from transformers.workout_transformer import WorkoutTransformer
    
    # Extract and transform data
    extractor = CSVExtractor('data/sample_workouts.csv')
    raw_data = extractor.extract_workouts()
    
    transformer = WorkoutTransformer()
    transformed_data = transformer.transform_csv_workouts(raw_data)
    
    # Load data
    loader = DatabaseLoader()
    clean_data = loader.check_duplicates(transformed_data)
    
    print(f"Records to load: {len(clean_data)}")
    success = loader.load_activities(clean_data)
    
    if success:
        print("Data loaded successfully!")
    else:
        print("Failed to load data")
