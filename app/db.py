import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Returns appropriate DB connection based on environment."""
    postgres_host = os.getenv("POSTGRES_HOST")
    
    if postgres_host and postgres_host != "localhost":
        # Production - use PostgreSQL
        import psycopg2
        return psycopg2.connect(
            host=postgres_host,
            port=os.getenv("POSTGRES_PORT", 5432),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            dbname=os.getenv("POSTGRES_DB")
        ), "postgres"
    else:
        # Local/Demo - use SQLite
        conn = sqlite3.connect("data/claims.db")
        return conn, "sqlite"

def get_table_name():
    """Returns correct table name based on DB type."""
    postgres_host = os.getenv("POSTGRES_HOST")
    if postgres_host and postgres_host != "localhost":
        return "claims.insurance_claims"
    return "insurance_claims"

def init_sqlite():
    """Initialize SQLite database from CSV if not exists."""
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists("data/claims.db"):
        print("Initializing SQLite database...")
        df = pd.read_csv("data/raw/claims.csv")
        conn = sqlite3.connect("data/claims.db")
        df.to_sql("insurance_claims", conn, if_exists="replace", index=False)
        conn.close()
        print(f"SQLite initialized with {len(df)} claims")
    else:
        print("SQLite database already exists")
