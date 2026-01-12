from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QComboBox, QLineEdit

from src.application.dto import Columns


class FilterFrame(QGroupBox):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter
        self._build_ui()

    def _on_column_changed(self):
        col = self.column_combo.currentData()
        self.presenter.set_filter_column(col)

        if col == Columns.HIRE_DATE:
            self.value_input.setPlaceholderText("ДД.ММ.ГГГГ (например, 19.10.2025)")
        elif col == Columns.SALARY:
            self.value_input.setPlaceholderText("Число (например, 50000 или 50000.50)")
        else:
            self.value_input.setPlaceholderText("Введите значение...")

    def _build_ui(self):
        self.setTitle("2. Настройка фильтрации")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel("Выберите столбец для фильтрации:"))

        self.column_combo = QComboBox()
        self.column_combo.addItem("-- Выберите колонку --", None)
        for c in Columns:
            self.column_combo.addItem(c.value, c)

        self.column_combo.currentIndexChanged.connect(self._on_column_changed)
        layout.addWidget(self.column_combo)

        layout.addWidget(QLabel("Введите значение для фильтрации:"))

        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Введите значение...")
        self.value_input.textChanged.connect(self.presenter.set_filter_value_raw)
        layout.addWidget(self.value_input)
