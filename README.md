# klad-connector

Единая библиотека для упрощённого взаимодействия с КЛАД (консолидированным логическим аналитическим хранилищем) в проектах BI.

**Ключевые возможности:**

- **Конфигурация через `.env`**: централизованное хранение строк подключения к Postgres и пути к DFS.
- **PostgresClient**: лёгкий API для выполнения запросов `read_sql` и записи `to_sql` через SQLAlchemy с поддержкой пулов соединений.
- **DFSClient**: надёжная загрузка и скачивание файлов в файловое хранилище DFS с автоматическим созданием директорий.
- **Единая обработка ошибок**: `ConfigError` при проблемах с конфигом и `ConnectionError` при сбоях соединения.
- **Гибкость**: работает и с реальными Postgres, и в режиме SQLite для локального демо.

---

## Содержание

1. [Требования](#требования)
2. [Установка](#установка)
3. [Настройка](#настройка)
4. [Принцип работы](#принцип-работы)
5. [Пример использования](#пример-использования)
6. [Структура проекта](#структура-проекта)
7. [Тестирование](#тестирование)
8. [Приватность репозитория](#приватность-репозитория)
9. [Contributing](#contributing)
10. [License](#license)

---

## Требования

- Python 3.10+
- Зависимости (из `requirements.txt`):
  - `python-dotenv`
  - `SQLAlchemy`
  - `pandas`
  - `psycopg2-binary` *(для Postgres)*
  - `jupyter` и `ipykernel` *(для демонстрации в Jupyter)*

## Установка

```bash
# Клонировать репозиторий
git clone https://github.com/your-org/klad-connector.git
cd klad-connector

# Создать виртуальное окружение и активировать
python3 -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
. .\.venv\Scripts\Activate.ps1

# Установить зависимости
pip install -r requirements.txt
```



## Настройка

Создайте в корне проекта файл `.env` с содержимым:

```dotenv
# Postgres-подключения для разных профилей
PG_DEV_URI=postgresql://user:pass@host:5432/dev_db
PG_TEST_URI=postgresql://user:pass@host:5432/test_db
PG_PRD_URI=postgresql://user:pass@host:5432/prod_db

# Локальный путь для DFS
dfs_root=C:/Users/you/projects/klad-connector/dfs
```

- Переменные `PG_<PROFILE>_URI` читаются методом `get_pg_uri(profile)`.
- `DFS_ROOT` используется в `get_dfs_root()`.  
- Любые опечатки в ключах вызовут `ConfigError`.

## Принцип работы

1. **Загрузка конфигурации**  
   При импорте `klad_connector.config` вызывается `load_dotenv()`, который считывает `.env` и загружает переменные окружения.

2. **PostgresClient**  
   - **Инициализация**: `get_pg_uri(profile)` возвращает строку подключения, из которой создаётся SQLAlchemy Engine с пулом соединений (`pool_pre_ping=True`).  
   - **Метод `connection()`**: контекстный менеджер, который открывает/закрывает соединение без утечек.  
   - **`read_sql(sql)`**: выполняет запрос и возвращает `pandas.DataFrame`.  
   - **`to_sql(df, table)`**: записывает DataFrame в указанный schema.table, используя pandas.

3. **DFSClient**  
   - **Инициализация**: берёт путь из `get_dfs_root()` и создаёт папку, если её нет.  
   - **`upload_file(local, remote)`**: копирует файл из локальной FS в папку DFS, создавая промежуточные каталоги.  
   - **`download_file(remote, local)`**: копирует файл из DFS в локальную директорию (по умолчанию `cwd`).  

4. **Обработка ошибок**  
   Все ошибки конфигурации генерируют `ConfigError`, а сбои при подключении или копировании — `ConnectionError`, что упрощает отлов и логирование.

---

## Пример использования

### Инициализация
```python
from klad_connector import PostgresClient, DFSClient

pg = PostgresClient(profile="dev")  # подключаемся к DEV
dfs = DFSClient()                  # корень DFS из .env
```

### Чтение из Postgres
```python
df = pg.read_sql("SELECT * FROM dim_clients LIMIT 5")
print(df)
```

### Запись в Postgres
```python
# допустим, у вас есть df_sales
df_sales = ...
pg.to_sql(df_sales, table="raw_sales", if_exists="append")
```

### Загрузка в DFS
```python
csv = "report.csv"
df.to_csv(csv, index=False)
dfs.upload_file(csv, "reports/report.csv")
```

### Скачивание из DFS
```python
dfs.download_file("reports/report.csv", "downloaded_report.csv")
import pandas as pd
print(pd.read_csv("downloaded_report.csv"))
```

---

## Структура проекта

```text
klad-connector/
├── .venv/               # виртуальное окружение
├── klad_connector/      # исходники библиотеки
│   ├── __init__.py
│   ├── config.py
│   ├── exceptions.py
│   ├── pg_client.py
│   └── dfs_client.py
├── dfs/                 # локальный пример DFS
├── tests/               # автотесты (pytest)
├── requirements.txt
├── .env                 # параметры подключения (не в Git)
├── README.md            # документация
└── klad_demo.ipynb      # демонстрационная тетрадка
```

---



