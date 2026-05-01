import pandas as pd
from sqlalchemy import text
from config.source_connection import get_sqlite_connection
from config.target_connection import get_postgres_engine


STAGING_SCHEMA = "staging"
CHUNK_SIZE = 50_000


def ensure_staging_schema(engine):
    with engine.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {STAGING_SCHEMA}"))


def get_source_tables(sqlite_conn):
    query = """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """
    tables_df = pd.read_sql_query(query, sqlite_conn)
    return tables_df["name"].tolist()


def load_table_to_staging(sqlite_conn, postgres_engine, table_name):
    query = f'SELECT * FROM "{table_name}"'

    total_rows = 0
    chunk_number = 0

    print(f"\nExtracting table: {table_name}")

    for chunk_df in pd.read_sql_query(query, sqlite_conn, chunksize=CHUNK_SIZE):
        chunk_number += 1

        if_exists_mode = "replace" if chunk_number == 1 else "append"

        chunk_df.to_sql(
            name=table_name,
            con=postgres_engine,
            schema=STAGING_SCHEMA,
            if_exists=if_exists_mode,
            index=False,
            method="multi"
        )

        total_rows += len(chunk_df)
        print(f"Loaded chunk {chunk_number}: {len(chunk_df)} rows")

    print(f"Finished {table_name}: {total_rows} rows loaded")


def extract_to_staging():
    sqlite_conn = get_sqlite_connection()
    postgres_engine = get_postgres_engine()

    try:
        ensure_staging_schema(postgres_engine)

        table_names = get_source_tables(sqlite_conn)

        print(f"Found {len(table_names)} source tables")

        for table_name in table_names:
            load_table_to_staging(
                sqlite_conn=sqlite_conn,
                postgres_engine=postgres_engine,
                table_name=table_name
            )

        print("\nExtraction completed successfully.")

    finally:
        sqlite_conn.close()
        postgres_engine.dispose()


if __name__ == "__main__":
    extract_to_staging()