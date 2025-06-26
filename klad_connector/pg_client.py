from contextlib import contextmanager
import pandas as pd
import sqlalchemy as sa
from .config import get_pg_uri
from .exceptions import ConnectionError

class PostgresClient:
    def __init__(self, profile: str = "dev"):
        uri = get_pg_uri(profile)
        try:
            self.engine = sa.create_engine(uri, pool_pre_ping=True)
        except Exception as e:
            raise ConnectionError(f"Engine создаётся с ошибкой: {e}")

    @contextmanager
    def connection(self):
        conn = self.engine.connect()
        try:
            yield conn
        finally:
            conn.close()

    def read_sql(self, sql: str, **kwargs) -> pd.DataFrame:
        try:
            with self.connection() as conn:
                return pd.read_sql(sql, conn, **kwargs)
        except Exception as e:
            raise ConnectionError(f"read_sql упал: {e}")

    def to_sql(self, df: pd.DataFrame, table: str,
               if_exists: str = "append", **kwargs):
        try:
            with self.connection() as conn:
                df.to_sql(name=table, con=conn,
                          if_exists=if_exists, index=False, **kwargs)
        except Exception as e:
            raise ConnectionError(f"to_sql упал: {e}")