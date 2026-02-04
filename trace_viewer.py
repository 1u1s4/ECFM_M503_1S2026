"""
Visualizador interactivo de trazas de recursión.
UI minimalista en blanco y negro con tipografía de consola.
"""

import sys
from io import StringIO
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSpinBox, QPushButton, QTextEdit, QFrame, QTabWidget, QLineEdit
)
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt


# === Lógica del factorial con traza ===

_recursion_depth = 0

def factorial(n: int, trace: bool = False) -> int:
    """Calcula el factorial usando recursión con traza opcional."""
    global _recursion_depth

    if n < 0:
        raise ValueError("El número debe ser no negativo")

    indent = "  " * _recursion_depth
    if trace:
        print(f"{indent}→ factorial({n})")

    if n == 0 or n == 1:
        if trace:
            print(f"{indent}← Caso base: factorial({n}) = 1")
        return 1

    _recursion_depth += 1
    result = n * factorial(n - 1, trace)
    _recursion_depth -= 1

    if trace:
        print(f"{indent}← factorial({n}) = {n} × factorial({n-1}) = {result}")

    return result


def capture_trace(n: int) -> tuple[str, int]:
    """Captura la traza de factorial en un string."""
    global _recursion_depth
    _recursion_depth = 0

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    result = factorial(n, trace=True)

    trace_output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    return trace_output, result


_merge_recursion_depth = 0


def merge_sort(arr: list[int], trace: bool = False) -> list[int]:
    """Ordena una lista usando merge sort con traza opcional."""
    global _merge_recursion_depth

    indent = "  " * _merge_recursion_depth
    if trace:
        print(f"{indent}→ merge_sort({arr})")

    # Caso base: listas de tamaño 0 o 1 ya están ordenadas
    if len(arr) <= 1:
        if trace:
            print(f"{indent}← Caso base: {arr}")
        return arr[:]

    mid = len(arr) // 2
    _merge_recursion_depth += 1
    left = merge_sort(arr[:mid], trace)
    right = merge_sort(arr[mid:], trace)
    _merge_recursion_depth -= 1

    # Fase de mezcla
    if trace:
        print(f"{indent} Mezclando {left} y {right}")

    merged: list[int] = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            merged.append(left[i])
            i += 1
        else:
            merged.append(right[j])
            j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])

    if trace:
        print(f"{indent}← Resultado: {merged}")

    return merged


def capture_merge_trace(numbers: list[int]) -> tuple[str, list[int]]:
    """Captura la traza de merge sort en un string."""
    global _merge_recursion_depth
    _merge_recursion_depth = 0

    old_stdout = sys.stdout
    sys.stdout = StringIO()

    result = merge_sort(numbers, trace=True)

    trace_output = sys.stdout.getvalue()
    sys.stdout = old_stdout

    return trace_output, result


# === Interfaz gráfica ===

class TraceViewer(QMainWindow):
    """Ventana principal del visualizador de trazas."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trace Viewer")
        self.setMinimumSize(600, 500)
        self.setup_style()
        self.setup_ui()

    def setup_style(self):
        """Configura el estilo minimalista blanco-negro."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #ffffff;
                color: #000000;
            }
            QLabel {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
                font-size: 14px;
                color: #000000;
            }
            QSpinBox {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
                font-size: 16px;
                padding: 8px 12px;
                border: 1px solid #000000;
                background-color: #ffffff;
                color: #000000;
                min-width: 80px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                background-color: #f0f0f0;
                width: 20px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e0e0e0;
            }
            QPushButton {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
                font-size: 14px;
                padding: 10px 24px;
                border: 1px solid #000000;
                background-color: #000000;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QPushButton:pressed {
                background-color: #555555;
            }
            QTextEdit {
                font-family: 'SF Mono', 'Monaco', 'Menlo', 'Consolas', monospace;
                font-size: 13px;
                line-height: 1.5;
                border: 1px solid #000000;
                background-color: #fafafa;
                color: #000000;
                padding: 16px;
            }
            QFrame#separator {
                background-color: #000000;
                max-height: 1px;
            }
        """)

    def setup_ui(self):
        """Construye la interfaz de usuario."""
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Título
        title = QLabel("TRACE VIEWER")
        title.setStyleSheet("font-size: 20px; font-weight: bold; letter-spacing: 4px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtítulo
        subtitle = QLabel("Visualización de llamadas recursivas")
        subtitle.setStyleSheet("font-size: 12px; color: #666666;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # Separador
        sep = QFrame()
        sep.setObjectName("separator")
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Tabs principales
        tabs = QTabWidget()
        layout.addWidget(tabs, 1)

        # === Tab: Factorial ===
        factorial_tab = QWidget()
        tabs.addTab(factorial_tab, "Factorial")

        fact_layout = QVBoxLayout(factorial_tab)
        fact_layout.setSpacing(16)

        # Controles factorial
        fact_controls = QHBoxLayout()
        fact_controls.setSpacing(16)

        fact_label = QLabel("n =")
        fact_label.setStyleSheet("font-size: 16px;")
        fact_controls.addWidget(fact_label)

        self.spin = QSpinBox()
        self.spin.setRange(0, 12)
        self.spin.setValue(5)
        fact_controls.addWidget(self.spin)

        fact_controls.addStretch()

        self.btn = QPushButton("EJECUTAR")
        self.btn.clicked.connect(self.run_trace)
        self.btn.setCursor(Qt.CursorShape.PointingHandCursor)
        fact_controls.addWidget(self.btn)

        fact_layout.addLayout(fact_controls)

        # Área de traza factorial
        self.trace_area = QTextEdit()
        self.trace_area.setReadOnly(True)
        self.trace_area.setPlaceholderText("La traza de factorial aparecerá aquí...")
        fact_layout.addWidget(self.trace_area, 1)

        # Resultado factorial
        self.result_label = QLabel("")
        self.result_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 12px; "
            "background-color: #f5f5f5; border: 1px solid #e0e0e0;"
        )
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fact_layout.addWidget(self.result_label)

        # === Tab: Merge Sort ===
        merge_tab = QWidget()
        tabs.addTab(merge_tab, "Merge Sort")

        merge_layout = QVBoxLayout(merge_tab)
        merge_layout.setSpacing(16)

        # Controles merge sort
        merge_controls = QVBoxLayout()
        merge_controls.setSpacing(8)

        merge_label = QLabel("Lista de números (separados por comas):")
        merge_label.setStyleSheet("font-size: 14px;")
        merge_controls.addWidget(merge_label)

        self.merge_input = QLineEdit()
        self.merge_input.setPlaceholderText("Ejemplo: 5, 2, 9, 1, 3")
        self.merge_input.setText("5, 2, 9, 1, 3")
        merge_controls.addWidget(self.merge_input)

        merge_btn_layout = QHBoxLayout()
        merge_btn_layout.addStretch()

        self.merge_btn = QPushButton("EJECUTAR MERGE SORT")
        self.merge_btn.clicked.connect(self.run_merge_trace)
        self.merge_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        merge_btn_layout.addWidget(self.merge_btn)

        merge_controls.addLayout(merge_btn_layout)
        merge_layout.addLayout(merge_controls)

        # Área de traza merge sort
        self.merge_trace_area = QTextEdit()
        self.merge_trace_area.setReadOnly(True)
        self.merge_trace_area.setPlaceholderText("La traza de merge sort aparecerá aquí...")
        merge_layout.addWidget(self.merge_trace_area, 1)

        # Resultado merge sort
        self.merge_result_label = QLabel("")
        self.merge_result_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 12px; "
            "background-color: #f5f5f5; border: 1px solid #e0e0e0;"
        )
        self.merge_result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        merge_layout.addWidget(self.merge_result_label)

        # Ejecutar con valor inicial en factorial
        self.run_trace()

    def run_trace(self):
        """Ejecuta el factorial y muestra la traza."""
        n = self.spin.value()
        trace_output, result = capture_trace(n)

        self.trace_area.setPlainText(trace_output)
        self.result_label.setText(f"factorial({n}) = {result}")

    def run_merge_trace(self):
        """Ejecuta merge sort y muestra la traza."""
        text = self.merge_input.text()
        try:
            numbers = [int(x.strip()) for x in text.split(",") if x.strip() != ""]
        except ValueError:
            self.merge_trace_area.setPlainText(
                "Error: asegúrate de ingresar solo enteros separados por comas."
            )
            self.merge_result_label.setText("")
            return

        trace_output, result = capture_merge_trace(numbers)

        self.merge_trace_area.setPlainText(trace_output)
        self.merge_result_label.setText(f"merge_sort({numbers}) = {result}")


def main():
    app = QApplication(sys.argv)

    # Fuente por defecto
    font = QFont("SF Mono, Monaco, Menlo, Consolas", 12)
    app.setFont(font)

    window = TraceViewer()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
