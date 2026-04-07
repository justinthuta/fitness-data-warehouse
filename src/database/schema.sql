-- Fitness Data Warehouse Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data sources table (tracks where data comes from)
CREATE TABLE IF NOT EXISTS data_sources (
    source_id SERIAL PRIMARY KEY,
    source_name VARCHAR(50) NOT NULL,  -- 'strava', 'fitbit', 'myfitnesspal', 'manual'
    description TEXT
);

-- Activities table (workouts, runs, rides, etc.)
CREATE TABLE IF NOT EXISTS activities (
    activity_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    source_id INTEGER REFERENCES data_sources(source_id),
    external_id VARCHAR(100),  -- ID from the original platform
    activity_type VARCHAR(50), -- 'run', 'ride', 'workout', 'walk', 'swim'
    activity_name VARCHAR(200),
    start_time TIMESTAMP,
    duration_seconds INTEGER,
    distance_meters REAL,
    calories_burned INTEGER,
    average_heart_rate INTEGER,
    max_heart_rate INTEGER,
    elevation_gain_meters REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, external_id)  -- Prevent duplicates from same source
);

-- Nutrition logs table
CREATE TABLE IF NOT EXISTS nutrition_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    source_id INTEGER REFERENCES data_sources(source_id),
    external_id VARCHAR(100),
    log_date DATE,
    meal_type VARCHAR(20), -- 'breakfast', 'lunch', 'dinner', 'snack'
    food_name VARCHAR(200),
    calories INTEGER,
    protein_grams REAL,
    carbs_grams REAL,
    fat_grams REAL,
    fiber_grams REAL,
    sodium_mg REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Body metrics table (weight, body composition, etc.)
CREATE TABLE IF NOT EXISTS body_metrics (
    metric_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    source_id INTEGER REFERENCES data_sources(source_id),
    metric_date DATE,
    weight_kg REAL,
    body_fat_percent REAL,
    muscle_mass_kg REAL,
    bmi REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sleep data table
CREATE TABLE IF NOT EXISTS sleep_logs (
    sleep_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    source_id INTEGER REFERENCES data_sources(source_id),
    external_id VARCHAR(100),
    sleep_date DATE,
    bedtime TIMESTAMP,
    wake_time TIMESTAMP,
    total_sleep_minutes INTEGER,
    deep_sleep_minutes INTEGER,
    light_sleep_minutes INTEGER,
    rem_sleep_minutes INTEGER,
    sleep_efficiency_percent REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial data sources
INSERT INTO data_sources (source_name, description) VALUES 
('strava', 'Strava fitness activities'),
('fitbit', 'Fitbit device data'),
('myfitnesspal', 'MyFitnessPal nutrition data'),
('apple_health', 'Apple Health app data'),
('manual', 'Manually entered data')
ON CONFLICT (source_name) DO NOTHING;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_activities_user_id ON activities(user_id);
CREATE INDEX IF NOT EXISTS idx_activities_start_time ON activities(start_time);
CREATE INDEX IF NOT EXISTS idx_activities_type ON activities(activity_type);
CREATE INDEX IF NOT EXISTS idx_nutrition_user_date ON nutrition_logs(user_id, log_date);
CREATE INDEX IF NOT EXISTS idx_body_metrics_user_date ON body_metrics(user_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_sleep_user_date ON sleep_logs(user_id, sleep_date);