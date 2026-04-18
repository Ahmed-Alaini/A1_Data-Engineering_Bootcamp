import csv
from pathlib import Path

from app.db import get_connection

BASE_DIR = Path(__file__).resolve().parents[2]
cars_csv = BASE_DIR / "data" / "processed" / "yemen_cars_cleaned.csv"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS cars_info (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    model INTEGER,
    posted_at TIMESTAMP,
    image_url TEXT,
    price NUMERIC,
    status TEXT,
    mileage INTEGER,
    location TEXT,
    country TEXT
);
"""

INSERT_SQL = """
INSERT INTO cars_info (
    name,
    description,
    model,
    posted_at,
    image_url,
    price,
    status,
    mileage,
    location,
    country
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
"""


def create_table():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_SQL)
        conn.commit()
        print("Table created successfully.")
    except Exception as e:
        conn.rollback()
        print("Error creating table:", e)
    finally:
        conn.close()



def load_csv(csv_file_path):
    conn = get_connection()
    try:
        with open(csv_file_path, mode="r", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            with conn.cursor() as cur:
                for row in reader:
                    cur.execute(
                        INSERT_SQL,
                        (
                            row["name"],
                            row["description"],
                            int(float(row["model"])) if row["model"] else None,
                            row["posted_at"] if row["posted_at"] else None,
                            row["image_url"],
                            float(row["price"]) if row["price"] else None,
                            row["status"],
                            int(float(row["mileage"])) if row["mileage"] else None,
                            row["location"],
                            row["country"]
                        )
                    )

        conn.commit()
        print("CSV data loaded successfully.")
    except Exception as e:
        conn.rollback()
        print("Error loading CSV:", e)
    finally:
        conn.close()

