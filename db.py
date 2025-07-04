from sqlalchemy import create_engine, Table, Column, Integer, Numeric, MetaData, TIMESTAMP, insert, delete, select
from sqlalchemy.exc import ArgumentError
from datetime import datetime
from dotenv import load_dotenv
import os
import logging
from urllib.parse import urlparse

# Load env variables
load_dotenv()

# Load from .env file
DB_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DB_URL}")

# Add error handling for missing DATABASE_URL
if not DB_URL:
    print("Warning: DATABASE_URL not found in environment variables.")
    print("Please create a .env file with your DATABASE_URL or set it as an environment variable.")
    print("Example: DATABASE_URL=postgresql://username:password@host:port/database")
    # Use a fallback SQLite database for development

# Validate URL format
try:
    parsed_url = urlparse(DB_URL)
    if not parsed_url.scheme or not parsed_url.hostname:
        raise ValueError("Invalid URL format")
    print(f"URL parsed successfully: {parsed_url.scheme}://{parsed_url.hostname}:{parsed_url.port}")
except Exception as e:
    print(f"URL parsing error: {e}")
    print("Using fallback SQLite database.")

# Create the SQLAlchemy engine
try:
    if DB_URL:
        engine = create_engine(DB_URL)
    else:
        engine = create_engine("sqlite:///fallback.db")
    print("Engine created successfully!")
except ArgumentError as e:
    print(f"Error creating engine: {e}")
    engine = create_engine("sqlite:///fallback.db")
    print("Fallback SQLite engine created.")

metadata = MetaData()

# Define the table
bankroll_history = Table("bankroll_history", metadata,
    Column("id", Integer, primary_key=True),
    Column("hand", Integer),
    Column("bet", Numeric),
    Column("equity", Numeric),
    Column("bankroll", Numeric),
    Column("created_at", TIMESTAMP, default=datetime.utcnow),
)

# Create tables if they don't exist
try:
    metadata.create_all(engine)
    print("Database tables created/verified successfully!")
except Exception as e:
    print(f"Error creating tables: {e}")

def save_hand(hand, bet, equity, bankroll):
    try:
        with engine.connect() as conn:
            conn.execute(insert(bankroll_history), [{
                "hand": hand,
                "bet": bet,
                "equity": equity,
                "bankroll": bankroll,
            }])
            conn.commit()
        print(f"Hand {hand} saved successfully!")
    except Exception as e:
        print(f"Error saving hand: {e}")
        raise

def get_hand_history():
    try:
        with engine.connect() as conn:
            result = conn.execute(bankroll_history.select().order_by(bankroll_history.c.hand))
            return result.fetchall()
    except Exception as e:
        print(f"Error getting hand history: {e}")
        return []

def clear_history():
    try:
        with engine.connect() as conn:
            conn.execute(delete(bankroll_history))
            conn.commit()
        print("History cleared successfully!")
    except Exception as e:
        print(f"Error clearing history: {e}")
