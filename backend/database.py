import json, sqlite3
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "roamly.db"

@contextmanager
def connection():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        yield db
        db.commit()
    finally:
        db.close()

def init_db():
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL,
          password_hash TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS trips(
          id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, city TEXT NOT NULL,
          start_date TEXT NOT NULL, days_count INTEGER NOT NULL, budget REAL NOT NULL,
          travelers TEXT NOT NULL, interests TEXT NOT NULL, itinerary TEXT NOT NULL,
          share_token TEXT UNIQUE, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
          FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
        """)

def trip_dict(row):
    data = dict(row)
    data["interests"] = json.loads(data["interests"])
    data["itinerary"] = json.loads(data["itinerary"])
    return data
