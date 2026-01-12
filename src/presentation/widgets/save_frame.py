import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QLabel, QHBoxLayout,
    QLineEdit, QPushButton, QFileDialog
)


class SaveFrame(QGroupBox):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter
        self._build_ui()

    def _select_target_file(self):
        default_name = "обработанный_файл.xlsx"
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл как",
            os.path.join(os.path.expanduser("~"), default_name),
            "Excel Files (*.xlsx);;All Files (*.*)",
        )
        if file_name:
            if not file_name.lower().endswith(".xlsx"):
                file_name += ".xlsx"
            self.path_input.setText(file_name)
            self.presenter.set_target_path(file_name)

    def _build_ui(self):
        self.setTitle("3. Сохранение результата")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel("Укажите, куда сохранить результат (.xlsx).")
        info.setWordWrap(True)
        layout.addWidget(info)

        row = QHBoxLayout()
        row.setSpacing(10)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Путь сохранения...")
        self.path_input.textChanged.connect(self.presenter.set_target_path)
        row.addWidget(self.path_input)

        btn = QPushButton("Обзор...")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(self._select_target_file)
        btn.setFixedWidth(120)
        row.addWidget(btn)

        layout.addLayout(row)
