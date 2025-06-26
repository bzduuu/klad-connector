# test_dfs.py
from klad_connector.dfs_client import DFSClient

dfs = DFSClient()
dfs.upload_file("test.txt", "demo/test_copy.txt")
dfs.download_file("demo/test_copy.txt", "downloaded_test.txt")
print("DFSClient OK")