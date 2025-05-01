"""
Initialize the database with tables for the Carbon Emission Calculator.
"""
from utils.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    engine = init_db()
    print(f"Database initialized successfully with connection: {engine.url}")