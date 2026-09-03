import sys
import os
import requests
import pandas as pd
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from auth.strava_client import get_valid_access_token

class StravaExtractor:
    def __init__(self):
        self.base_url = 'https://www.strava.com/api/v3'
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/strava_extractor.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def extract_activities(self, per_page=30):
        """Pull recent activities from Strava API"""
        try:
            access_token = get_valid_access_token()
            headers = {'Authorization': f'Bearer {access_token}'}
            
            response = requests.get(
                f'{self.base_url}/athlete/activities',
                headers=headers,
                params={'per_page': per_page}
            )
            
            if response.status_code != 200:
                raise Exception(f"Strava API error: {response.status_code} - {response.text}")
            
            activities = response.json()
            self.logger.info(f"Retrieved {len(activities)} activities from Strava")
            
            df = pd.DataFrame(activities)
            return df
            
        except Exception as e:
            self.logger.error(f"Error extracting Strava activities: {e}")
            raise

if __name__ == "__main__":
    extractor = StravaExtractor()
    data = extractor.extract_activities()
    print(f"\nRetrieved {len(data)} activities")
    print("\nColumns available:")
    print(list(data.columns))
    print("\nFirst activity preview:")
    print(data[['name', 'type', 'start_date', 'distance', 'moving_time']].head())
