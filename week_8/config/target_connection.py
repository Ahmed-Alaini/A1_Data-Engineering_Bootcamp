from sqlalchemy import create_engine


USER = "postgres"
PASSWORD = "postgres"
HOST = "localhost"
PORT = "5434"
DB = "olist_dwh"


def get_postgres_engine():
    #Create SQLAlchemy engine for PostgreSQL target database.
    
    connection_string = (
        f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"
    )

    return create_engine(connection_string)