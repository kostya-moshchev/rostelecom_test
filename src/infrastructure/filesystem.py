from __future__ import annotations

import os
from pathlib import Path


class LocalFileSystem:
    def normalize_path(self, path: str) -> str:
        if not path:
            return path
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = Path.cwd() / p
        return str(p.resolve())

    def exists(self, path: str) -> bool:
        return Path(path).exists()

    def is_file(self, path: str) -> bool:
        return Path(path).is_file()

    def can_read(self, path: str) -> bool:
        return os.access(path, os.R_OK)

    def ensure_parent_dir(self, file_path: str) -> None:
        parent = Path(file_path).parent
        parent.mkdir(parents=True, exist_ok=True)

    def can_write_dir_of(self, file_path: str) -> bool:
        parent = Path(file_path).parent
        return os.access(str(parent), os.W_OK)

    def get_size_bytes(self, path: str) -> int:
        return os.path.getsize(path)
