import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLabel, QMessageBox
)

from src.application.interactors.process_excel_interactor import ProcessExcelInteractor
from src.infrastructure.filesystem import LocalFileSystem
from src.infrastructure.openpyxl_reader import OpenPyxlExcelReader
from src.infrastructure.openpyxl_writer import OpenPyxlExcelWriter
from src.presentation.presenter import MainPresenter
from src.presentation.widgets.file_frame import FileFrame
from src.presentation.widgets.filter_frame import FilterFrame
from src.presentation.widgets.save_frame import SaveFrame
from src.presentation.widgets.execute_frame import ExecuteFrame


class MainWindow(QMainWindow):
    def __init__(self, interactor=None):
        super().__init__()

        self.presenter = MainPresenter(interactor)

        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("Обработчик Excel файлов")

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setSpacing(12)

        title = QLabel("Обработчик Excel файлов")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel { font-size: 18px; font-weight: bold; }
        """)
        layout.addWidget(title)

        layout.addWidget(FileFrame(self, self.presenter))
        layout.addWidget(FilterFrame(self, self.presenter))
        layout.addWidget(SaveFrame(self, self.presenter))
        layout.addWidget(ExecuteFrame(self, self.presenter))

        layout.addStretch()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите выйти?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        event.accept() if reply == QMessageBox.StandardButton.Yes else event.ignore()


def main():
    app = QApplication([])

    fs = LocalFileSystem()
    reader = OpenPyxlExcelReader()
    writer = OpenPyxlExcelWriter()
    interactor = ProcessExcelInteractor(fs=fs, reader=reader, writer=writer)

    window = MainWindow(interactor=interactor)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
