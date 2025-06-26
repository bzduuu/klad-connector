
from smb.SMBConnection import SMBConnection
import os
import shutil
from .exceptions import ConnectionError
from .config import get_dfs_root

class DFSClient:
    def __init__(self, user, password, dfs_remote_name, dfs_domain):
        """
        Конструктор для подключения к удалённому файловому хранилищу через SMB.

        :param user: Имя пользователя для подключения
        :param password: Пароль для подключения
        :param dfs_remote_name: Имя удалённого сервера
        :param dfs_domain: Домен для подключения
        """
        self.conn = SMBConnection(
            username=user,
            password=password,
            my_name='gpnconnect',  # Имя подключения
            remote_name=dfs_remote_name,
            domain=dfs_domain,
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        self.dfs_remote_name = dfs_remote_name
        self.dfs_root = get_dfs_root()

    def connect(self):
        """Подключение к SMB-серверу"""
        self.conn.connect(self.dfs_remote_name, port=445)

    def write(self, dfs_folder_share, remote_file_path, local_file_path):
        """
        Записывает локальный файл в удалённую файловую систему.

        :param dfs_folder_share: удаленный ресурс, куда загружается файл.
        :param remote_file_path: Путь к файлу на удалённом ресурсе.
        :param local_file_path: полный путь к локальному файлу.
        """
        try:
            with open(local_file_path, 'rb') as localfile:
                self.conn.storeFile(dfs_folder_share, remote_file_path, localfile)
        except Exception as e:
            raise ConnectionError(f"Ошибка при загрузке файла в DFS: {e}")

    def read(self, dfs_folder_share, remote_file_path, local_file_path):
        """
        Чтение файла с удалённого хранилища и сохранение его.

        :param dfs_folder_share: удаленный ресурс, откуда читаем файл.
        :param remote_file_path: Путь к файлу на удалённом ресурсе.
        :param local_file_path: Путь к локальному файлу для сохранения.
        """
        try:
            with open(local_file_path, 'wb') as localfile:
                self.conn.retrieveFile(dfs_folder_share, remote_file_path, localfile)
        except Exception as e:
            raise ConnectionError(f"Ошибка при скачивании файла из DFS: {e}")

    def create_directory(self, dfs_folder_share, directory_path):
        """
        Создаёт директорию на удалённом сервере.

        :param dfs_folder_share: удаленный ресурс, где создается директория.
        :param directory_path: Путь к создаваемой директории.
        """
        try:
            self.conn.createDirectory(dfs_folder_share, directory_path)
        except Exception as e:
            print(f'Ошибка при создании директории {directory_path}: {e}')

    def list_files(self, dfs_folder_share, directory_path=''):
        """
        Возвращает список файлов и директорий в указанной папке на удалённом сервере.

        :param dfs_folder_share: Удаленный ресурс, где выполняется операция.
        :param directory_path: Папка внутри ресурса (опционально).
        :return: Список файлов и директорий.
        """
        base_path = f"/{dfs_folder_share}/{directory_path}".rstrip('/')
        result = []

        for entry in self.conn.listPath(dfs_folder_share, directory_path):
            if entry.filename not in ('.', '..'):
                full_path = os.path.join(base_path, entry.filename)
                result.append(full_path)
        return result

    def list_smb_files(self, dfs_folder_share, directory_path=''):
        """
        Возвращает список файлов в указанной папке на удалённом сервере через SMB.

        :param dfs_folder_share: удаленный ресурс, где выполняется операция.
        :param directory_path: Папка внутри ресурса (опционально).
        :return: Список файлов в указанной папке.
        """
        return self.conn.listPath(dfs_folder_share, directory_path)

    def _recursive_read_folder(self, dfs_folder_share, remote_path, local_output_dir):
        """
        Рекурсивное чтение и сохранение всех файлов из удалённой папки.

        :param dfs_folder_share: удаленный ресурс, где выполняется операция.
        :param remote_path: Текущая удалённая папка.
        :param local_output_dir: Локальная директория для сохранения.
        """
        entries = self.list_smb_files(dfs_folder_share, remote_path)

        for entry in entries:
            # Игнорируем служебные записи '.' и '..'
            if entry.filename in ('.', '..'):
                continue

            # Формирование полного пути
            full_remote_path = os.path.join(remote_path, entry.filename)
            local_path = os.path.join(local_output_dir, entry.filename)

            if entry.isDirectory:
                # Создание локальной папки и рекурсия для вложенных элементов
                os.makedirs(local_path, exist_ok=True)
                self._recursive_read_folder(dfs_folder_share, full_remote_path, local_path)
            else:
                # Скачивание файла
                self.read(dfs_folder_share, full_remote_path, local_path)

    def read_folder(self, dfs_folder_share, remote_root_folder, local_output_dir):
        """
        Рекурсивное чтение и сохранение всех файлов и папок из удалённой папки и её подпапок.

        :param dfs_folder_share: Удаленный ресурс (шар), откуда считываем файлы.
        :param remote_root_folder: Корневая папка на удалённом сервере.
        :param local_output_dir: Локальная директория для сохранения всех файлов.
        """
        self._recursive_read_folder(dfs_folder_share, remote_root_folder, local_output_dir)