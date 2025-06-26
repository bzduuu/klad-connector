from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import urllib.parse
from .config import get_pg_uri
from .exceptions import ConnectionError


class PostgresClient:
    def __init__(self, host=None, port=None, dbname=None, user=None, password=None, profile="dev"):
        """
        Инициализация подключения к базе данных PostgreSQL с использованием SQLAlchemy и psycopg2.
        """

        # Если параметры не переданы, берём из .env
        if not all([host, port, dbname, user, password]):
            uri = get_pg_uri(profile)
            parsed_uri = urllib.parse.urlparse(uri)
            host = parsed_uri.hostname
            port = parsed_uri.port
            dbname = parsed_uri.path[1:]  # убираем слэш
            user = parsed_uri.username
            password = parsed_uri.password

        # Экранируем пароль
        quoted_password = urllib.parse.quote_plus(password)

        # Строка подключения через SQLAlchemy
        conn_string = f'postgresql://{user}:{quoted_password}@{host}:{port}/{dbname}'
        
        try:
            # Используем SQLAlchemy для подключения и работы с pandas
            self.engine = create_engine(conn_string)
            # Создаём соединение через psycopg2 для выполнения запросов
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
                    return cur.fetchall()  # Получаем все строки
                else:
                    self.conn.commit()  # Совершаем commit в БД
                    return None
        except psycopg2.Error as err:
            raise ConnectionError(f"Ошибка выполнения запроса: {err}")

    def read_pandas(self, query):
        """
        Читаем данные в DataFrame используя SQLAlchemy engine
        """
        try:
            data = pd.read_sql(query, con=self.engine)
            return data
        except Exception as e:
            raise ConnectionError(f"Ошибка при чтении данных из базы: {e}")

    def write_to_table(self, df, table_name, mode='append', schema=None):
        """
        Записывает данные из DataFrame в указанную таблицу базы данных.
        """
        try:
            with self.engine.begin() as connection:  # Автоматически коммитит транзакцию
                df.to_sql(table_name, con=connection, index=False, if_exists=mode, schema=schema)
        except Exception as e:
            raise ConnectionError(f"Ошибка при записи данных в таблицу '{table_name}': {e}")

    def close(self):
        """
        Закрывает соединение с базой данных.
        """
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()