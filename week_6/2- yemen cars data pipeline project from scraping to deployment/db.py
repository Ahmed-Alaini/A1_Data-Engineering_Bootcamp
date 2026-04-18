import psycopg2

def get_connection():

    return psycopg2.connect(
        host="localhost",
        database="cars",
        user="postgres",
        password="postgres",
        port=5434
    )