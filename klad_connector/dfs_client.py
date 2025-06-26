from smb.SMBConnection import SMBConnection
import os
import shutil
from .exceptions import ConnectionError

class DFSClient:
    def __init__(self, user, password, dfs_remote_name, dfs_domain):
        """Конструктор для подключения к удалённому файловому хранилищу через SMB."""
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

    def connect(self):
        """Подключение к SMB-серверу."""
        self.conn.connect(self.dfs_remote_name, port=445)

    def write(self, dfs_folder_share, remote_file_path, local_file_path):
        """Записывает файл на удалённый сервер."""
        with open(local_file_path, 'rb') as localfile:
            self.conn.storeFile(dfs_folder_share, remote_file_path, localfile)

    def read(self, dfs_folder_share, remote_file_path, local_file_path):
        """Чтение файла с удалённого сервера."""
        with open(local_file_path, 'wb') as localfile:
            self.conn.retrieveFile(dfs_folder_share, remote_file_path, localfile)

    def list_files(self, dfs_folder_share, directory_path=''):
        """Возвращает список файлов в удалённой папке."""
        return self.conn.listPath(dfs_folder_share, directory_path)