from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox


class ExecuteFrame(QGroupBox):
    def __init__(self, parent, presenter):
        super().__init__(parent)
        self.presenter = presenter
        self._build_ui()

    def _run(self):
        result = self.presenter.run()

        if result.success:
            QMessageBox.information(
                self,
                "Готово",
                f"{result.message}\n\nФайл успешно сохранён:\n{result.output_path}",
            )
        else:
            QMessageBox.critical(
                self,
                "Ошибка",
                result.message,
            )

    def _exit(self):
        self.window().close()

    def _build_ui(self):
        self.setTitle("4. Выполнение обработки")

        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        row = QHBoxLayout()
        row.setSpacing(12)

        run_btn = QPushButton("Выполнить обработку")
        run_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        run_btn.clicked.connect(self._run)
        row.addWidget(run_btn)

        exit_btn = QPushButton("Выход")
        exit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        exit_btn.clicked.connect(self._exit)
        row.addWidget(exit_btn)

        layout.addLayout(row)
