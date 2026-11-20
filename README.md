# Fitness Data Warehouse

A Python and PostgreSQL ETL pipeline that pulls my fitness data into one database. I wear different devices and use different apps, so my data was scattered. I wanted to see everything in one place.

Right now the pipeline works with two sources: **live Strava activities through the Strava API** and **CSV workout files**. More sources are planned (see Roadmap).

## How it works

```
Strava API or CSV file  ->  Extract  ->  Transform  ->  Check duplicates  ->  Load into PostgreSQL
```

1. **Extract**: `StravaExtractor` calls the Strava API and returns recent activities. `CSVExtractor` reads workout CSV files.
2. **Transform**: `StravaTransformer` and `WorkoutTransformer` clean the raw data into one format that matches the database schema.
3. **Check duplicates**: `DatabaseLoader.check_duplicates()` skips activities that are already stored, using the source and the external activity ID.
4. **Load**: `DatabaseLoader.load_activities()` writes new rows into PostgreSQL with pandas and SQLAlchemy.

## Strava integration

* Uses **OAuth 2.0** (`activity:read_all` scope) to connect to a Strava account
* Saves tokens locally in `config/strava_tokens.json` (gitignored, never committed)
* **Refreshes the access token automatically** when it is about to expire
* Pulls recent activities and stores type, name, start time, duration, distance, heart rate and elevation
* Running the pipeline twice does not create duplicate rows

## Tech stack

* **Database**: PostgreSQL
* **Language**: Python 3.9+
* **Data processing**: pandas, SQLAlchemy
* **Database driver**: psycopg2
* **API calls**: requests
* **Config**: python-dotenv

## Database schema

Six tables in `src/database/schema.sql`:

| Table | Purpose |
| --- | --- |
| `users` | Who the data belongs to |
| `data_sources` | Where data came from (Strava, manual entry, and so on) |
| `activities` | Workouts, runs and rides with metrics. Unique on source and external ID |
| `nutrition_logs` | Food intake and macros |
| `body_metrics` | Weight and body composition over time |
| `sleep_logs` | Sleep duration and quality |

The activities table is fully used by the pipeline today. The nutrition, body metrics and sleep tables are ready for future sources.

## Project structure

```
fitness-data-warehouse/
├── src/
│   ├── auth/            # Strava OAuth: authorize, token exchange, auto refresh
│   ├── database/        # Connection and schema.sql
│   ├── extractors/      # strava_extractor.py, csv_extractor.py
│   ├── transformers/    # strava_transformer.py, workout_transformer.py
│   ├── loaders/         # database_loader.py
│   └── pipelines/       # strava_pipeline.py (full Strava ETL run)
├── config/              # .env.example
├── data/                # sample_workouts.csv
└── logs/                # created at runtime
```

## Setup

1. **Clone and enter the project**
```bash
git clone https://github.com/justinthuta/fitness-data-warehouse.git && cd fitness-data-warehouse
```

2. **Create a virtual environment and install dependencies**
```bash
python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```
On Windows, activate with `venv\Scripts\activate` instead.

3. **Add your settings**
```bash
cp config/.env.example config/.env
```
Then edit `config/.env` with your PostgreSQL details. For Strava, create an app at strava.com/settings/api and add your client ID and secret.

4. **Create the database tables**
```bash
python3 src/database/connection.py
```

## Run it

**CSV sample data**
```bash
python3 src/loaders/database_loader.py
```

**Strava (first time only: connect your account)**
```bash
python3 src/auth/strava_auth.py
```
Approve access in the browser, copy the `code` from the redirect URL, then run:
```bash
python3 src/auth/strava_token_exchange.py
```

**Strava (pull activities and load them)**
```bash
python3 src/pipelines/strava_pipeline.py
```

## Known limitations

* The Strava pull gets the latest 30 activities only. There is no pagination or full history sync yet.
* The Strava transformer assumes user ID 1 and source ID 1 (Strava) from the seed data.
* Calories are often missing from the Strava list endpoint, so they are filled with 0.
* No automated tests yet.

## Roadmap

- [x] CSV extraction and loading
- [x] Strava API integration with OAuth 2.0 and automatic token refresh
- [x] Duplicate detection
- [ ] Pagination and full Strava history
- [ ] Garmin Connect, Whoop, COROS, Apple Health and MyFitnessPal sources
- [ ] Unit tests
- [ ] Analytics dashboard
- [ ] Scheduling with Airflow
- [ ] Cloud deployment

## Author

Min Thuta Aung, Computer Science, Queens College (CUNY)
