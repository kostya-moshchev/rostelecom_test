from dataclasses import dataclass
from typing import Optional

from src.application.dto import ProcessingRequestDTO, ProcessingResultDTO, Columns


@dataclass
class PresenterState:
    source_path: str = ""
    target_path: str = ""
    filter_column: Optional[Columns] = None
    filter_value_raw: str = ""


class MainPresenter:
    def __init__(self, interactor):
        self._interactor = interactor
        self.state = PresenterState()

    def set_source_path(self, path: str) -> None:
        self.state.source_path = path or ""

    def set_target_path(self, path: str) -> None:
        self.state.target_path = path or ""

    def set_filter_column(self, col: Optional[Columns]) -> None:
        self.state.filter_column = col


    def set_filter_value_raw(self, raw: str) -> None:
        self.state.filter_value_raw = raw or ""

    def run(self) -> ProcessingResultDTO:
        if self.state.filter_column is None:
            return ProcessingResultDTO(
                success=False,
                message="Выберите столбец для фильтрации",
                error_code="ui_filter_column_missing",
            )

        req = ProcessingRequestDTO(
            source_path=self.state.source_path,
            target_path=self.state.target_path,
            filter_column=self.state.filter_column,
            filter_value_raw=self.state.filter_value_raw,
        )

        result: ProcessingResultDTO = self._interactor(req)

        return result
