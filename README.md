# klad-connector
Библиотека для подключения к КЛАД
# klad-connector

Единая библиотека для упрощённого взаимодействия с КЛАД (консолидированным логическим аналитическим хранилищем) в проектах BI.

Ключевые возможности:

- **Конфигурация через **``: хранение строк подключения к Postgres и пути к DFS.
- **PostgresClient**: простой API для выполнения запросов `read_sql` и записи `to_sql` через SQLAlchemy.
- **DFSClient**: загрузка и выгрузка файлов в файловое хранилище DFS с автоматическим созданием директорий.
- **Обработка ошибок**: единая иерархия исключений `ConfigError` и `ConnectionError`.

---

## Содержание

1. [Требования](#требования)
2. [Установка](#установка)
3. [Настройка](#настройка)
4. [Пример использования](#пример-использования)
   - [Инициализация](#инициализация)
   - [Чтение из Postgres](#чтение-из-postgres)
   - [Запись в Postgres](#запись-в-postgres)
   - [Загрузка в DFS](#загрузка-в-dfs)
   - [Скачивание из DFS](#скачивание-из-dfs)
5. [Структура проекта](#структура-проекта)
6. [Тесты](#тесты)
7. [Contributing](#contributing)
8. [License](#license)

---

## Требования

- Python 3.10+
- Установленные зависимости:
  - `python-dotenv`
  - `SQLAlchemy`
  - `pandas`
  - `jupyter` *(для демо-тетрадки)*
  - `ipykernel` *(для Jupyter-ядра)*

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/bzduuu/klad-connector.git
cd klad-connector

# Создать и активировать виртуальное окружение
python3 -m venv .venv
# на Linux/macOS
source .venv/bin/activate
# на Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt
```

В `requirements.txt` должно быть:

```
python-dotenv>=1.0
SQLAlchemy>=2.0
pandas>=2.0
jupyter
ipykernel
psycopg2-binary    # драйвер для Postgres
```

## Настройка

Создайте файл `.env` в корне проекта с параметрами подключения:

```dotenv
# Настройки подключения к Postgres
PG_DEV_URI=postgresql://username:password@hostname:5432/dbname
PG_TEST_URI=postgresql://username:password@hostname:5432/test_db
PG_PRD_URI=postgresql://username:password@hostname:5432/prod_db

# Путь к корню DFS
DFS_ROOT=C:/path/to/your/dfs
```

Параметры:

- `PG_<profile>_URI` — строка подключения для профилей `dev`, `test`, `prd`.
- `DFS_ROOT` — абсолютный путь к локальной папке, которая будет использоваться в качестве DFS.

---

## Пример использования

### Инициализация

```python
from klad_connector import PostgresClient, DFSClient

# Инициализируем клиента Postgres (профиль dev)
pg = PostgresClient(profile="dev")

# Инициализируем клиента DFS (использует переменную DFS_ROOT)
dfs = DFSClient()
```

### Чтение из Postgres

```python
# Выполняем SQL-запрос и получаем pandas.DataFrame
df = pg.read_sql("SELECT * FROM dim_clients LIMIT 10")
print(df.head())
```

### Запись в Postgres

```python
# Отправляем DataFrame в таблицу raw_sales
pg.to_sql(df_sales, table="raw_sales", if_exists="append")
```

### Загрузка в DFS

```python
# Экспортируем DataFrame в CSV
csv_path = "clients_report.csv"
df.to_csv(csv_path, index=False)

# Загружаем файл в DFS по заданному пути
dfs.upload_file(csv_path, "fin/reports/clients_report.csv")
```

### Скачивание из DFS

```python
# Скачиваем файл из DFS в текущую директорию
dfs.download_file("fin/reports/clients_report.csv", "downloaded_report.csv")

# Читаем скачанный CSV
import pandas as pd

report_df = pd.read_csv("downloaded_report.csv")
print(report_df.head())
```

---

## Структура проекта

```
klad-connector/
├── .venv/               # виртуальное окружение
├── klad_connector/      # исходники библиотеки
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── pg_client.py
│   └── dfs_client.py
├── dfs/                 # пример «локального» DFS
├── tests/               # автотесты (pytest)
├── requirements.txt
├── .env
├── README.md
└── klad_demo.ipynb      # демонстрационная тетрадка
```

---
##Пока не сделано:
## Тесты

1. Установите `pytest`:
   ```bash
   pip install pytest
   ```
2. Запустите в корне проекта:
   ```bash
   pytest -q
   ```
3. Автотесты проверяют:
   - Корректность загрузки конфигурации
   - Работу `PostgresClient` в режиме SQLite
   - Работа `DFSClient` с локальной папкой

---



