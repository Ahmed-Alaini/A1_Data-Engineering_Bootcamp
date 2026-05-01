from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parent.parent
SQLITE_DB_PATH = BASE_DIR / "source" / "olist.sqlite"


def get_sqlite_connection():
    
    #Create a connection to the SQLite source database.
  
    if not SQLITE_DB_PATH.exists():
        raise FileNotFoundError(f"SQLite database not found at: {SQLITE_DB_PATH}")

    return sqlite3.connect(SQLITE_DB_PATH)