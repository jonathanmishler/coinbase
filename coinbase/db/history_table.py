import psycopg
from psycopg import sql
from .settings import Settings

config = Settings()

def create_history_table(cur: psycopg.Cursor, coin_id: str, price_precision: int = 10, price_scale: int = 5):
    sql_str = sql.SQL("""
            CREATE TABLE {table} (
                timestamp TIMESTMAP PRIMARY KEY,
                low {price_type},
                high {price_type},
                open {price_type},
                close {price_type},
                volumne DOUBLE PRECISION
                )
            """).format(
                table = sql.Identifier(f"{coin_id}_history"),
                price_type = sql.Identifier(f"NUMERIC({price_precision},{price_scale})")
            )

with psycopg.connect(config.conn_str) as conn:
    with conn.cursor() as cur:
        # Execute a command: this creates a new table
        cur.execute("""
            CREATE TABLE test (
                id serial PRIMARY KEY,
                num integer,
                data text)
            """)

        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no SQL injections!)
        cur.execute(
            "INSERT INTO test (num, data) VALUES (%s, %s)",
            (100, "abc'def"))

        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM test")
        cur.fetchone()
        # will return (1, 100, "abc'def")

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        for record in cur:
            print(record)

        # Make the changes to the database persistent
        conn.commit()