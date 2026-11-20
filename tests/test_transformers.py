import os
import sys
import unittest

import pandas as pd

ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.join(ROOT, 'src'))

from extractors.csv_extractor import CSVExtractor
from transformers.strava_transformer import StravaTransformer, OUTPUT_COLUMNS
from transformers.workout_transformer import WorkoutTransformer
from auth.strava_token_exchange import extract_code


class TestWorkoutTransformer(unittest.TestCase):
    def setUp(self):
        raw = CSVExtractor(os.path.join(ROOT, 'data', 'sample_workouts.csv')).extract_workouts()
        self.raw = raw
        self.out = WorkoutTransformer().transform_csv_workouts(raw, source_id=6, user_id=2)

    def test_row_count_and_ids(self):
        self.assertEqual(len(self.out), len(self.raw))
        self.assertTrue((self.out['source_id'] == 6).all())
        self.assertTrue((self.out['user_id'] == 2).all())

    def test_units_converted(self):
        first = self.raw.iloc[0]
        self.assertEqual(self.out.iloc[0]['duration_seconds'], int(first['duration_minutes'] * 60))
        self.assertAlmostEqual(self.out.iloc[0]['distance_meters'], first['distance_km'] * 1000, places=3)

    def test_external_ids_are_unique(self):
        self.assertEqual(self.out['external_id'].nunique(), len(self.out))

    def test_same_file_gives_same_ids(self):
        again = WorkoutTransformer().transform_csv_workouts(self.raw, source_id=6, user_id=2)
        self.assertEqual(list(again['external_id']), list(self.out['external_id']))

    def test_missing_optional_columns(self):
        slim = self.raw[['date', 'activity_type', 'duration_minutes']]
        out = WorkoutTransformer().transform_csv_workouts(slim, source_id=6)
        self.assertEqual(len(out), len(slim))
        self.assertTrue(out['average_heart_rate'].isna().all())


class TestStravaTransformer(unittest.TestCase):
    def sample(self):
        return pd.DataFrame([
            {'id': 111, 'type': 'Run', 'name': 'Morning Run', 'start_date': '2026-11-01T12:00:00Z',
             'moving_time': 1800, 'distance': 5000.0, 'total_elevation_gain': 20.5,
             'average_heartrate': 150.4, 'max_heartrate': 175.0},
            {'id': 222, 'type': 'Walk', 'name': 'Evening Walk', 'start_date': '2026-11-02T22:30:00Z',
             'moving_time': 900, 'distance': 1200.0, 'total_elevation_gain': 0.0},
        ])

    def test_normal_activities(self):
        out = StravaTransformer().transform_activities(self.sample(), source_id=1, user_id=1)
        self.assertEqual(list(out['external_id']), ['111', '222'])
        self.assertEqual(out.iloc[0]['average_heart_rate'], 150)
        self.assertTrue(pd.isna(out.iloc[1]['average_heart_rate']))  # no heart rate stays empty
        self.assertIsNone(out['start_time'].dt.tz)  # timezone removed for the database

    def test_missing_columns_do_not_crash(self):
        bare = pd.DataFrame([{'id': 333, 'start_date': '2026-11-03T08:00:00Z'}])
        out = StravaTransformer().transform_activities(bare, source_id=1)
        self.assertEqual(len(out), 1)
        self.assertEqual(out.iloc[0]['duration_seconds'], 0)

    def test_empty_input(self):
        out = StravaTransformer().transform_activities(pd.DataFrame(), source_id=1)
        self.assertEqual(len(out), 0)
        self.assertEqual(list(out.columns), OUTPUT_COLUMNS)

    def test_output_matches_workout_columns(self):
        strava = StravaTransformer().transform_activities(self.sample(), source_id=1)
        csv_raw = CSVExtractor(os.path.join(ROOT, 'data', 'sample_workouts.csv')).extract_workouts()
        csv_out = WorkoutTransformer().transform_csv_workouts(csv_raw, source_id=6)
        self.assertEqual(set(strava.columns), set(csv_out.columns))


class TestTokenExchangeHelper(unittest.TestCase):
    def test_bare_code(self):
        self.assertEqual(extract_code('  abc123  '), 'abc123')

    def test_full_url(self):
        url = 'http://localhost/exchange_token?state=&code=abc123&scope=read,activity:read_all'
        self.assertEqual(extract_code(url), 'abc123')

    def test_url_without_code(self):
        self.assertIsNone(extract_code('http://localhost/exchange_token?error=access_denied'))


if __name__ == '__main__':
    unittest.main()
