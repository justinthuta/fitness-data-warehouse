import os
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv('config/.env')

class DatabaseConnection:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.port = os.getenv('DB_PORT', '5432')
        self.database = os.getenv('DB_NAME', 'fitness_warehouse')
        self.username = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD') or ''
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Set up logging for database operations"""
        os.makedirs('logs', exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/database.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    def get_connection(self):
        """Get raw psycopg2 connection"""
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            self.logger.info("Database connection established successfully")
            return conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        try:
            # URL.create handles special characters (like @ or #) in the password
            url = URL.create(
                "postgresql+psycopg2",
                username=self.username,
                password=self.password,
                host=self.host,
                port=int(self.port),
                database=self.database
            )
            engine = create_engine(url)
            self.logger.info("SQLAlchemy engine created successfully")
            return engine
        except Exception as e:
            self.logger.error(f"Failed to create database engine: {e}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                self.logger.info(f"Connected to: {version}")
                return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def setup_database(self):
        """Create the fitness_warehouse database if it doesn't exist"""
        try:
            temp_conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='postgres',
                user=self.username,
                password=self.password
            )
            temp_conn.autocommit = True
            cursor = temp_conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (self.database,))
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f'CREATE DATABASE "{self.database}"')
                self.logger.info(f"Created database: {self.database}")
            else:
                self.logger.info(f"Database {self.database} already exists")
                
            cursor.close()
            temp_conn.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup database: {e}")
            return False
    
    def create_tables(self):
        """Create all tables using the schema file"""
        try:
            with open('src/database/schema.sql', 'r') as f:
                schema_sql = f.read()
            
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(schema_sql)
            conn.commit()
            cursor.close()
            conn.close()
            
            self.logger.info("Database tables created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")
            return False

if __name__ == "__main__":
    db = DatabaseConnection()

    print("Testing database connection...")

    connected = db.test_connection()
    if not connected:
        print("Database connection failed. Trying to create the database...")
        if db.setup_database():
            connected = db.test_connection()

    if not connected:
        print("Could not connect. Check PostgreSQL is running and config/.env is correct.")
        raise SystemExit(1)

    print("Database connection successful!")

    print("Creating tables and seed data...")
    if db.create_tables():
        print("Done! Tables are ready.")
    else:
        print("Failed to create tables. See logs/database.log for details.")
        raise SystemExit(1)