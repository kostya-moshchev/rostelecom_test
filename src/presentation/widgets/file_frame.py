import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog
)


class FileFrame(QGroupBox):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter
        self._build_ui()

    def _select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите Excel файл",
            os.path.expanduser("~"),
            "Excel Files (*.xlsx);;All Files (*.*)",
        )
        if file_name:
            self.path_input.setText(file_name)
            self.presenter.set_source_path(file_name)

    def _build_ui(self):
        self.setTitle("1. Выбор файла")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel("Выберите исходный Excel файл (.xlsx) для обработки.")
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Путь к исходному файлу...")
        self.path_input.textChanged.connect(self.presenter.set_source_path)
        row.addWidget(self.path_input)

        btn = QPushButton("Выбрать...")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._select_file)
        btn.setFixedWidth(120)
        row.addWidget(btn)

        layout.addLayout(row)
