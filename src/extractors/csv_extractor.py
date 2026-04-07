import pandas as pd
from datetime import datetime
import logging
import os

class CSVExtractor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/extractor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def extract_workouts(self):
        """Extract workout data from CSV file"""
        try:
            # Read CSV
            df = pd.read_csv(self.file_path)
            
            self.logger.info(f"Loaded {len(df)} records from {self.file_path}")
            
            # Basic data validation
            required_columns = ['date', 'activity_type', 'duration_minutes']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert date column
            df['date'] = pd.to_datetime(df['date'])
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting data: {e}")
            raise

if __name__ == "__main__":
    extractor = CSVExtractor('data/sample_workouts.csv')
    data = extractor.extract_workouts()
    print("Sample data extracted:")
    print(data.head())
    print(f"Data shape: {data.shape}")
