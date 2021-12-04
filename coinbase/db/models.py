import json
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from psycopg import sql
from . import utils


class CoinHistory(BaseModel):
    timestamp: datetime = Field(..., sql_str="TIMESTAMP PRIMARY KEY")
    low: Decimal = Field(..., sql_str="NUMERIC(10,5)")
    high: Decimal = Field(..., sql_str="NUMERIC(10,5)")
    open: Decimal = Field(..., sql_str="NUMERIC(10,5)")
    close: Decimal = Field(..., sql_str="NUMERIC(10,5)")
    volume: float = Field(..., sql_str="DOUBLE PRECISION")

    @classmethod
    def from_coinbase(cls, txt_resp: str) -> list:
        """Creates a list of models from the coinbase text response"""
        # parse every element as a string and let pydantic do the type conversion explicitly from a string
        data = json.loads(txt_resp, parse_float=str, parse_int=str, parse_constant=str)
        return [
            cls.parse_obj(
                {key: value for key, value in zip(cls.__fields__.keys(), row)}
            )
            for row in data
        ]

    def as_tuple(self) -> tuple:
        """Returns a tuple with all the field values to be inserted into a SQL statement"""
        return self.timestamp, self.low, self.high, self.open, self.close, self.volume

    @classmethod
    def insert_str(cls, coin_id: str) -> sql.Composed:
        """Uses the utils.insert_rows_str method to create an INSERT statement from
        the coin_id and the field names from the pydantic model
        """
        table_name = cls.table_name(coin_id)
        col_names = cls.__fields__.keys()
        return utils.insert_str(table_name, col_names)

    @classmethod
    def create_table_str(cls, coin_id: str) -> sql.Composed:
        """Uses the utils.create_table_str method to create a CREATE TABLE statement
        from the coin_id and the field names and sql_str attribute from the pydantic model
        """
        table_name = cls.table_name(coin_id)
        cols = [(k, v.get("sql_str")) for k, v in cls.schema()["properties"].items()]
        return utils.create_table_str(table_name, cols)

    @staticmethod
    def table_name(coin_id: str) -> str:
        """Returns the nomralized sql table name for the given coin_id"""
        return (f"{coin_id}_history").lower().replace("-", "_")
