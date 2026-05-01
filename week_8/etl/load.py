from sqlalchemy import text


DWH_SCHEMA = "dwh"


def table_exists(engine, table_name):
    query = text("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = :schema_name
              AND table_name = :table_name
        );
    """)

    with engine.begin() as conn:
        return conn.execute(
            query,
            {
                "schema_name": DWH_SCHEMA,
                "table_name": table_name
            }
        ).scalar()


def truncate_table(engine, table_name):
    if not table_exists(engine, table_name):
        raise RuntimeError(f"Table {DWH_SCHEMA}.{table_name} does not exist")

    with engine.begin() as conn:
        conn.execute(
            text(
                f"TRUNCATE TABLE {DWH_SCHEMA}.{table_name} "
                "RESTART IDENTITY CASCADE"
            )
        )

    print(f"Truncated {DWH_SCHEMA}.{table_name}")


def load_dataframe(df, table_name, engine):
    df.to_sql(
        name=table_name,
        con=engine,
        schema=DWH_SCHEMA,
        if_exists="append",
        index=False,
        method="multi"
    )

    print(f"Loaded {len(df)} rows into {DWH_SCHEMA}.{table_name}")


def reload_table(df, table_name, engine):
    truncate_table(engine, table_name)
    load_dataframe(df, table_name, engine)