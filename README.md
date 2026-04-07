# Fitness Data Warehouse

A complete ETL pipeline for collecting, processing, and analyzing fitness data from multiple sources.

## Architecture

This project implements a 3-tier data warehouse architecture:
- **Data Layer**: PostgreSQL database with normalized schema
- **Processing Layer**: ETL pipeline with Extract-Transform-Load components
- **Analytics Layer**: SQL queries and data analysis capabilities

## Tech Stack

- **Database**: PostgreSQL
- **Backend**: Python 3.9+
- **Data Processing**: pandas, SQLAlchemy
- **Database Connection**: psycopg2
- **Environment Management**: python-dotenv

## Features

- Multi-source data integration (CSV, ready for API expansion)
- Duplicate detection and data validation
- Comprehensive fitness metrics tracking
- Modular, scalable design following data engineering best practices

## Database Schema

```sql
-- Core tables for fitness data
- users: User management and authentication
- data_sources: Track data origins (Strava, Fitbit, manual entry)
- activities: Workouts, runs, bike rides with metrics
- nutrition_logs: Food intake and macro tracking
- body_metrics: Weight, body composition over time
- sleep_logs: Sleep quality and duration analysis
```

## Project Structure

```
fitness-data-warehouse/
├── src/
│   ├── database/          # Database connection and schema
│   ├── extractors/        # Data extraction components
│   ├── transformers/      # Data transformation logic
│   └── loaders/          # Data loading utilities
├── config/               # Configuration files
├── data/                 # Sample datasets
└── logs/                 # Application logs
```

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/justinthuta/fitness-data-warehouse.git
   cd fitness-data-warehouse
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   ```bash
   cp config/.env.example config/.env
   # Edit config/.env with your PostgreSQL credentials
   ```

5. **Initialize database**
   ```bash
   python3 src/database/connection.py
   ```

6. **Run sample ETL pipeline**
   ```bash
   python3 src/loaders/database_loader.py
   ```

## Usage Example

```python
# Extract data from CSV
extractor = CSVExtractor('data/sample_workouts.csv')
raw_data = extractor.extract_workouts()

# Transform to database format
transformer = WorkoutTransformer()
clean_data = transformer.transform_csv_workouts(raw_data)

# Load to database
loader = DatabaseLoader()
loader.load_activities(clean_data)
```

## Future Enhancements

- [ ] Strava API integration
- [ ] Fitbit API integration
- [ ] Real-time data streaming
- [ ] Analytics dashboard
- [ ] Performance metrics calculation
- [ ] Data visualization components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details