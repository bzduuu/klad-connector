# klad_connector/dfs_client.py
from smb.SMBConnection import SMBConnection
import os
import shutil
from .exceptions import ConnectionError
from .config import get_dfs_root

class DFSClient:
    def __init__(self, user, password, dfs_remote_name, dfs_domain):
        self.conn = SMBConnection(
            username=user,
            password=password,
            my_name='gpnconnect',  # Наименование подключения
            remote_name=dfs_remote_name,
            domain=dfs_domain,
            use_ntlm_v2=True,
            is_direct_tcp=True
        )
        self.dfs_remote_name = dfs_remote_name
        self.dfs_root = get_dfs_root()

    def connect(self):
        """Подключение к удалённому серверу по порту 445"""
        self.conn.connect(self.dfs_remote_name, port=445)

    def write(self, dfs_folder_share, remote_file_path, local_file_path):
        """Записывает файл на удалённый сервер"""
        with open(local_file_path, 'rb') as localfile:
            self.conn.storeFile(dfs_folder_share, remote_file_path, localfile)

    def read(self, dfs_folder_share, remote_file_path, local_file_path):
        """Чтение файла с удалённого сервера"""
        with open(local_file_path, 'wb') as localfile:
            self.conn.retrieveFile(dfs_folder_share, remote_file_path, localfile)

    def create_directory(self, dfs_folder_share, directory_path):
        """Создаёт директорию на удалённом сервере"""
        try:
            self.conn.createDirectory(dfs_folder_share, directory_path)
        except Exception as e:
            print(f'Ошибка при создании директории {directory_path}: {e}')

    def list_files(self, dfs_folder_share, directory_path=''):
        """Возвращает список файлов в удалённой папке"""
        base_path = f"/{dfs_folder_share}/{directory_path}".rstrip('/')
        result = []
        for entry in self.conn.listPath(dfs_folder_share, directory_path):
            if entry.filename not in ('.', '..'):
                full_path = os.path.join(base_path, entry.filename)
                result.append(full_path)
        return result

    def list_smb_files(self, dfs_folder_share, directory_path=''):
        """Возвращает список файлов в удалённой папке SMB"""
        return self.conn.listPath(dfs_folder_share, directory_path)

    def _recursive_read_folder(self, dfs_folder_share, remote_path, local_output_dir):
        """Рекурсивное чтение файлов из папки"""
        entries = self.list_smb_files(dfs_folder_share, remote_path)
        for entry in entries:
            if entry.filename in ('.', '..'):
                continue
            full_remote_path = os.path.join(remote_path, entry.filename)
            local_path = os.path.join(local_output_dir, entry.filename)
            if entry.isDirectory:
                os.makedirs(local_path, exist_ok=True)
                self._recursive_read_folder(dfs_folder_share, full_remote_path, local_path)
            else:
                self.read(dfs_folder_share, full_remote_path, local_path)

    def read_folder(self, dfs_folder_share, remote_root_folder, local_output_dir):
        """Рекурсивное чтение и сохранение файлов из удалённой папки"""
        self._recursive_read_folder(dfs_folder_share, remote_root_folder, local_output_dir)