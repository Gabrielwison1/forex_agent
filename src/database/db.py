import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create Engine
engine = create_engine(DATABASE_URL)

# Verify Connection
def check_db_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print(f"Database Connection Successful: {result.fetchone()}")
            return True
    except Exception as e:
        print(f"Database Connection Failed: {e}")
        return False

if __name__ == "__main__":
    check_db_connection()
