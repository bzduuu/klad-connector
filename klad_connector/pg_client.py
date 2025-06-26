# klad_connector/pg_client.py
from sqlalchemy import create_engine
import psycopg2
import urllib.parse
import pandas as pd
from .config import get_pg_uri
from .exceptions import ConnectionError

class PostgresClient:
    def __init__(self, profile="dev"):
        """
        Подключение к базе данных PostgreSQL с использованием SQLAlchemy и psycopg2.
        """
        uri = get_pg_uri(profile)
        quoted_password = urllib.parse.quote_plus(uri.split(":")[2])  # Экранируем пароль
        conn_string = f'postgresql://{uri.split(":")[1]}:{quoted_password}@{uri.split(":")[3]}:{uri.split(":")[4]}'
        
        try:
            self.engine = create_engine(conn_string)
            self.conn = psycopg2.connect(conn_string)
        except Exception as err:
            raise ConnectionError(f"Ошибка подключения к базе данных: {err}")

    def execute(self, query, params=None, fetch=False):
        """
        Выполняет SQL-запрос с возможностью возвращения результатов.
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                else:
                    self.conn.commit()
                    return None
        except psycopg2.Error as err:
            raise RuntimeError(f"Ошибка выполнения запроса: {err}")

    def read_pandas(self, query):
        """
        Читаем данные в DataFrame используя SQLAlchemy engine
        """
        data = pd.read_sql(query, con=self.engine)
        return data

    def write_to_table(self, df, table_name, mode='append', schema=None):
        """
        Записывает данные из DataFrame в указанную таблицу базы данных.
        """
        try:
            with self.engine.begin() as connection:
                df.to_sql(table_name, con=connection, index=False, if_exists=mode, schema=schema)
        except Exception as e:
            raise RuntimeError(f"Ошибка при записи данных в таблицу '{table_name}': {e}")

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()