import shutil
from pathlib import Path
from .config import get_dfs_root
from .exceptions import ConnectionError

class DFSClient:
    def __init__(self, root: Path | None = None):
        try:
            self.root = root or get_dfs_root()
            Path(self.root).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConnectionError(f"DFS_ROOT недоступен: {e}")

    def upload_file(self, local_path: str | Path, remote_path: str | Path):
        src = Path(local_path)
        dst = Path(self.root) / remote_path
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✓ {src.name} → {dst}")
        except Exception as e:
            raise ConnectionError(f"upload_file упал: {e}")

    def download_file(self, remote_path: str | Path,
                      local_path: str | Path | None = None):
        src = Path(self.root) / remote_path
        dest = Path(local_path) if local_path else Path.cwd() / src.name
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            print(f"✓ {src.name} ← {src}")
        except Exception as e:
            raise ConnectionError(f"download_file упал: {e}")