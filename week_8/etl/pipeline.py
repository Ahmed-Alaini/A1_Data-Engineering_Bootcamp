from pathlib import Path
from sqlalchemy import text

from config.target_connection import get_postgres_engine
from etl.extract import extract_to_staging
from etl.load import reload_table
from etl.transform import (
    build_dim_date,
    build_dim_geolocation,
    build_dim_products,
    build_dim_order_status,
    build_dim_payment_type,
    build_dim_lead_origin,
    build_dim_lead_profile,
    build_dim_business_segment,
    build_dim_customers,
    build_dim_sellers,
    build_fact_order_items,
    build_fact_payments,
    build_fact_delivery_performance,
    build_fact_reviews,
    build_fact_seller_leads,
)


BASE_DIR = Path(__file__).resolve().parent.parent
DDL_PATH = BASE_DIR / "sql" / "create_dwh_tables.sql"


def run_sql_file(engine, file_path):
    if not file_path.exists():
        raise FileNotFoundError(f"SQL file not found: {file_path}")

    sql = file_path.read_text(encoding="utf-8")

    with engine.begin() as conn:
        conn.execute(text(sql))

    print(f"Executed SQL file: {file_path}")


def run_pipeline():
    print("Starting ETL pipeline...")

    engine = get_postgres_engine()

    try:
        print("\nStep 1: Creating schemas and DWH tables...")
        run_sql_file(engine, DDL_PATH)

    finally:
        engine.dispose()

    print("\nStep 2: Extracting SQLite data to staging...")
    extract_to_staging()

    engine = get_postgres_engine()

    try:
        print("\nStep 3: Building and loading independent dimensions...")

        reload_table(build_dim_date(engine), "dim_date", engine)
        reload_table(build_dim_geolocation(engine), "dim_geolocation", engine)
        reload_table(build_dim_products(engine), "dim_products", engine)
        reload_table(build_dim_order_status(engine), "dim_order_status", engine)
        reload_table(build_dim_payment_type(engine), "dim_payment_type", engine)

        print("\nStep 4: Building and loading lead dimensions...")

        reload_table(build_dim_lead_origin(engine), "dim_lead_origin", engine)
        reload_table(build_dim_lead_profile(engine), "dim_lead_profile", engine)
        reload_table(build_dim_business_segment(engine), "dim_business_segment", engine)

        print("\nStep 5: Building and loading dependent dimensions...")

        reload_table(build_dim_customers(engine), "dim_customers", engine)
        reload_table(build_dim_sellers(engine), "dim_sellers", engine)

        print("\nStep 6: Building and loading facts...")

        reload_table(build_fact_order_items(engine), "fact_order_items", engine)
        reload_table(build_fact_payments(engine), "fact_payments", engine)
        reload_table(build_fact_delivery_performance(engine), "fact_delivery_performance", engine)
        reload_table(build_fact_reviews(engine), "fact_reviews", engine)
        reload_table(build_fact_seller_leads(engine), "fact_seller_leads", engine)

        print("\nETL pipeline completed successfully.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    run_pipeline()