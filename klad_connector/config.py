import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()  # считываем .env

class ConfigError(Exception):
    """Ошибки при чтении конфигурации."""
    pass

def get_pg_uri(profile: str = "dev") -> str:
    key = f"PG_{profile.upper()}_URI"
    uri = os.getenv(key)
    if not uri:
        raise ConfigError(f"Переменная окружения {key} не найдена")
    return uri

def get_dfs_root() -> Path:
    root = os.getenv("DFS_ROOT", "/home/default/persistent")
    return Path(root)