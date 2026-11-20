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
        loader = DatabaseLoader()
        user_id = loader.get_or_create_user()
        source_id = loader.get_source_id('strava')

        logger.info("Starting Strava extraction...")
        extractor = StravaExtractor()
        raw_data = extractor.extract_activities()

        if len(raw_data) == 0:
            logger.info("Strava returned no activities.")
            return

        logger.info("Starting transformation...")
        transformer = StravaTransformer()
        transformed_data = transformer.transform_activities(raw_data, source_id=source_id, user_id=user_id)

        logger.info("Starting loading...")
        clean_data = loader.check_duplicates(transformed_data)

        if len(clean_data) > 0:
            success = loader.load_activities(clean_data)
            if success:
                logger.info(f"Pipeline completed! Loaded {len(clean_data)} new Strava activities.")
            else:
                logger.error("Pipeline failed during loading.")
                sys.exit(1)
        else:
            logger.info("No new activities to load (all duplicates).")

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_strava_etl_pipeline()
