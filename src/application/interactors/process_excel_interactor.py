from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Sequence, Dict, Optional, List, Tuple

from src.application.dto import ProcessingRequestDTO, ProcessingResultDTO, Columns
from src.application.interface import FileSystemPort, ExcelReaderPort, ExcelWriterPort


@dataclass
class ProcessExcelInteractor:
    fs: FileSystemPort
    reader: ExcelReaderPort
    writer: ExcelWriterPort
    max_size_bytes: int = 50 * 1024 * 1024

    def __call__(self, request: ProcessingRequestDTO) -> ProcessingResultDTO:
        prepared_or_error = self._prepare_request(request)
        if isinstance(prepared_or_error, ProcessingResultDTO):
            return prepared_or_error
        req = prepared_or_error

        rows_or_error = self._read_rows(req.source_path)
        if isinstance(rows_or_error, ProcessingResultDTO):
            return rows_or_error
        rows = rows_or_error

        required_headers = self._required_headers()
        header_or_error = self._locate_header(rows, required_headers)
        if isinstance(header_or_error, ProcessingResultDTO):
            return header_or_error
        col_index, header_row_idx = header_or_error

        filtered_or_error = self._filter_rows(
            rows=rows,
            header_row_idx=header_row_idx,
            col_index=col_index,
            request=req,
            required_headers=required_headers,
        )
        if isinstance(filtered_or_error, ProcessingResultDTO):
            return filtered_or_error
        filtered_rows = filtered_or_error

        write_error = self._write_output(req.target_path, required_headers, filtered_rows)
        if write_error is not None:
            return write_error

        return ProcessingResultDTO(True, "Документ обработан", output_path=req.target_path)


    def _prepare_request(self, request: ProcessingRequestDTO) -> ProcessingRequestDTO | ProcessingResultDTO:
        if not request.source_path.strip():
            return ProcessingResultDTO(False, "Не указан путь к исходному файлу", error_code="source_missing")
        if not request.target_path.strip():
            return ProcessingResultDTO(False, "Не указан путь для сохранения результата", error_code="target_missing")
        if not request.filter_value_raw.strip():
            return ProcessingResultDTO(False, "Не указано значение для фильтрации", error_code="filter_value_missing")

        source = self.fs.normalize_path(request.source_path)
        target = self.fs.normalize_path(request.target_path)

        if not source.lower().endswith(".xlsx"):
            return ProcessingResultDTO(False, "Поддерживаются только файлы Excel (*.xlsx)", error_code="bad_extension")
        if not self.fs.exists(source):
            return ProcessingResultDTO(False, f"Файл не найден: {source}", error_code="source_not_found")
        if not self.fs.is_file(source):
            return ProcessingResultDTO(False, f"Указанный путь не является файлом: {source}", error_code="source_not_file")
        if not self.fs.can_read(source):
            return ProcessingResultDTO(False, f"Нет прав на чтение файла: {source}", error_code="no_read_permission")

        size = self.fs.get_size_bytes(source)
        if size == 0:
            return ProcessingResultDTO(False, "Файл пустой", error_code="empty_file")
        if size > self.max_size_bytes:
            mb = size / (1024 * 1024)
            return ProcessingResultDTO(False, f"Файл слишком большой: {mb:.1f}MB (максимум 50MB)", error_code="too_large")

        try:
            self.fs.ensure_parent_dir(target)
        except Exception as e:
            return ProcessingResultDTO(False, f"Не удалось создать директорию назначения: {e}", error_code="target_dir_create_failed")
        if not self.fs.can_write_dir_of(target):
            return ProcessingResultDTO(False, "Нет прав на запись в директорию назначения", error_code="no_write_permission")

        parsed_or_error = self._parse_filter_value(request.filter_column, request.filter_value_raw)
        if isinstance(parsed_or_error, ProcessingResultDTO):
            return parsed_or_error

        return ProcessingRequestDTO(
            source_path=source,
            target_path=target,
            filter_column=request.filter_column,
            filter_value_raw=request.filter_value_raw,
            filter_value=parsed_or_error,
        )

    def _read_rows(self, source_path: str) -> List[Sequence[Any]] | ProcessingResultDTO:
        try:
            rows = list(self.reader.iter_rows(source_path))
        except Exception as e:
            return ProcessingResultDTO(False, f"Ошибка при чтении Excel: {e}", error_code="excel_read_failed")

        if not rows:
            return ProcessingResultDTO(False, "Файл пустой", error_code="empty_file")

        return rows

    def _locate_header(
        self,
        rows: Sequence[Sequence[Any]],
        required_headers: Sequence[str],
    ) -> Tuple[Dict[str, int], int] | ProcessingResultDTO:
        info = self._find_header_row(rows, required_headers)
        if info is None:
            return ProcessingResultDTO(
                False,
                "Не найдены обязательные столбцы в файле (или заголовок отсутствует)",
                error_code="header_not_found",
            )
        return info

    def _filter_rows(
        self,
        *,
        rows: Sequence[Sequence[Any]],
        header_row_idx: int,
        col_index: Dict[str, int],
        request: ProcessingRequestDTO,
        required_headers: Sequence[str],
    ) -> List[List[Any]] | ProcessingResultDTO:
        filter_header = request.filter_column.value
        if filter_header not in col_index:
            return ProcessingResultDTO(
                False,
                f"Столбец для фильтрации '{filter_header}' не найден в заголовке",
                error_code="filter_column_not_found",
            )

        filter_col_i = col_index[filter_header]
        parsed_filter_value = request.filter_value

        out: List[List[Any]] = []
        for row in rows[header_row_idx + 1 :]:
            cell_value = row[filter_col_i] if filter_col_i < len(row) else None
            if self._compare_values(cell_value, parsed_filter_value, request.filter_column):
                out_row: List[Any] = []
                for h in required_headers:
                    idx = col_index[h]
                    out_row.append(row[idx] if idx < len(row) else None)
                out.append(out_row)

        if not out:
            return ProcessingResultDTO(
                False,
                f"Нет совпадений: '{request.filter_value_raw}' в колонке '{filter_header}'",
                error_code="no_matches",
            )

        return out

    def _write_output(
        self,
        target_path: str,
        headers: Sequence[str],
        rows: Sequence[Sequence[Any]],
    ) -> Optional[ProcessingResultDTO]:
        try:
            self.writer.write_table(
                target_path=target_path,
                headers=headers,
                rows=rows,
                generated_at_iso=datetime.now().isoformat(timespec="minutes"),
            )
            return None
        except Exception as e:
            return ProcessingResultDTO(False, f"Ошибка при сохранении Excel: {e}", error_code="excel_write_failed")


    def _required_headers(self) -> List[str]:
        return [c.value for c in Columns]

    def _parse_filter_value(self, column: Columns, raw: str) -> Any | ProcessingResultDTO:
        raw = raw.strip()

        if column == Columns.SALARY:
            try:
                value = float(raw.replace(",", "."))
            except ValueError:
                return ProcessingResultDTO(False, "Зарплата должна быть числом (например 50000 или 50000.50)", error_code="salary_not_number")

            if value <= 0:
                return ProcessingResultDTO(False, "Зарплата должна быть положительным числом", error_code="salary_not_positive")
            return value

        if column == Columns.HIRE_DATE:
            try:
                return datetime.strptime(raw, "%d.%m.%Y")
            except ValueError:
                return ProcessingResultDTO(False, "Неверный формат даты. Используйте ДД.ММ.ГГГГ (например 19.10.2025)", error_code="date_bad_format")

        return raw

    def _find_header_row(
        self,
        rows: Sequence[Sequence[Any]],
        required_headers: Sequence[str],
    ) -> Optional[Tuple[Dict[str, int], int]]:
        req = set(required_headers)

        for idx0, row in enumerate(rows):
            if not row:
                continue
            row_set = {cell for cell in row if cell is not None}
            if req.issubset(row_set):
                row_list = list(row)
                mapping: Dict[str, int] = {}
                for h in required_headers:
                    try:
                        mapping[h] = row_list.index(h)
                    except ValueError:
                        return None
                return mapping, idx0

        return None

    def _compare_values(self, cell_value: Any, filter_value: Any, column: Columns) -> bool:
        if cell_value is None and filter_value is None:
            return True
        if cell_value is None or filter_value is None:
            return False

        if column == Columns.SALARY:
            try:
                return float(cell_value) == float(filter_value)
            except (ValueError, TypeError):
                return False

        if column == Columns.HIRE_DATE:
            if isinstance(cell_value, datetime) and isinstance(filter_value, datetime):
                return cell_value.date() == filter_value.date()
            return str(cell_value).strip() == str(filter_value).strip()

        if isinstance(cell_value, str) and isinstance(filter_value, str):
            return cell_value.strip().lower() == filter_value.strip().lower()

        try:
            return float(cell_value) == float(filter_value)
        except (ValueError, TypeError):
            pass

        return str(cell_value).strip().lower() == str(filter_value).strip().lower()
