import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.db import check_db_connection

def test_connection():
    print("Testing PostgreSQL Connection...")
    if check_db_connection():
        print("PASS: Connected to PostgreSQL Docker Container.")
    else:
        print("FAIL: Could not connect to Database.")
        sys.exit(1)

if __name__ == "__main__":
    test_connection()
