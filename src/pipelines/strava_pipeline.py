import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from extractors.strava_extractor import StravaExtractor
from transformers.strava_transformer import StravaTransformer
from loaders.database_loader import DatabaseLoader
import logging

def run_strava_etl_pipeline():
    """Complete ETL pipeline: Extract from Strava -> Transform -> Load to PostgreSQL"""
    
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    try:
        logger.info("Starting Strava extraction...")
        extractor = StravaExtractor()
        raw_data = extractor.extract_activities()
        
        logger.info("Starting transformation...")
        transformer = StravaTransformer()
        transformed_data = transformer.transform_activities(raw_data)
        
        logger.info("Starting loading...")
        loader = DatabaseLoader()
        clean_data = loader.check_duplicates(transformed_data)
        
        if len(clean_data) > 0:
            success = loader.load_activities(clean_data)
            if success:
                logger.info(f"Pipeline completed! Loaded {len(clean_data)} new Strava activities.")
            else:
                logger.error("Pipeline failed during loading.")
        else:
            logger.info("No new activities to load (all duplicates).")
            
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")

if __name__ == "__main__":
    run_strava_etl_pipeline()
