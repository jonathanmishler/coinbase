from typing import List, Tuple
from psycopg import sql


def insert_str(table_name: str, col_names: list) -> sql.Composed:
    """Creates a INSERT sql.composed statement from the table name and column names"""
    sql_str = sql.SQL("INSERT INTO {table} ({cols}) VALUES ({placeholders})").format(
        table=sql.Identifier(table_name),
        cols=sql.SQL(", ").join(map(sql.Identifier, col_names)),
        placeholders=sql.SQL(", ").join(sql.Placeholder() * len(col_names)),
    )
    return sql_str


def create_table_str(table_name: str, cols: List[Tuple[str, str]]) -> sql.Composed:
    """Creates a CREATE TABLE sql.composed statement from the table name and a tuple
    with the (column name, column SQL datetype and contraints if any)"""
    cols = [(sql.Identifier(col[0]), sql.SQL(col[1])) for col in cols]
    sql_str = sql.SQL("CREATE TABLE IF NOT EXISTS {table} ({cols})").format(
        table=sql.Identifier(table_name),
        cols=sql.SQL(", ").join([sql.SQL(" ").join(col) for col in cols]),
    )
    return sql_str
