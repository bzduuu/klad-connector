class KladError(Exception):
    """Базовый класс ошибок к библиотеки Klad Connector."""
    pass

class ConfigError(KladError):
    """Ошибки при чтении конфигурации."""
    pass

class ConnectionError(KladError):
    """Ошибки при соединении с Postgres или DFS."""
    pass