from typing import Protocol, Iterable, Sequence, Any


class FileSystemPort(Protocol):
    def normalize_path(self, path: str) -> str: ...
    def exists(self, path: str) -> bool: ...
    def is_file(self, path: str) -> bool: ...
    def can_read(self, path: str) -> bool: ...

    def ensure_parent_dir(self, file_path: str) -> None: ...
    def can_write_dir_of(self, file_path: str) -> bool: ...

    def get_size_bytes(self, path: str) -> int: ...


class ExcelReaderPort(Protocol):
    def iter_rows(self, source_path: str) -> Iterable[Sequence[Any]]: ...


class ExcelWriterPort(Protocol):
    def write_table(
        self,
        target_path: str,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
        *,
        generated_at_iso: str,
        source_type_label: str = "Excel файл",
        sheet_title: str = "Отфильтрованные данные",
    ) -> None: ...
