# test_config.py
from klad_connector.config import get_pg_uri, get_dfs_root
from klad_connector.pg_client import PostgresClient
from klad_connector.dfs_client import DFSClient

print("PG DEV URI  =", get_pg_uri("dev"))
print("DFS_ROOT   =", get_dfs_root())

# Проверяем простой SQL-запрос (для этого в PG_DEV_URI должна быть рабочая БД)
pg = PostgresClient()
print("SQL SELECT:", pg.read_sql("SELECT 1 AS test").to_dict())

# Проверяем копирование файла
dfs = DFSClient()
dfs.upload_file("README.md", "tests/README_copy.md")