from dataclasses import dataclass, replace
from enum import Enum
from typing import Optional, Any


class Columns(Enum):
    FIO = "ФИО"
    POSITION = "Должность"
    DEPARTMENT = "Отдел"
    HIRE_DATE = "Дата найма"
    SALARY = "Зарплата"


@dataclass(frozen=True)
class ProcessingRequestDTO:
    source_path: str
    target_path: str
    filter_column: Columns
    filter_value_raw: str

    filter_value: Optional[Any] = None

    def with_parsed_filter_value(self, value: Any) -> "ProcessingRequestDTO":
        return replace(self, filter_value=value)


@dataclass(frozen=True)
class ProcessingResultDTO:
    success: bool
    message: str
    output_path: Optional[str] = None
    error_code: Optional[str] = None