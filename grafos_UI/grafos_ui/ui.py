from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from .controller import SimulationController
from .domain import GraphConfig
from .gpu import detect_compute_device
from .styles import APP_STYLESHEET
from .widgets import AlgorithmPanel, PanelFrame, build_algorithm_styles


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.controller = SimulationController()
        self.device_info = detect_compute_device()
        self.algorithm_styles = build_algorithm_styles()
        self.algorithm_order = ("bfs", "dfs", "dijkstra", "random")
        self.panels: dict[str, AlgorithmPanel] = {}
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)

        self.setWindowTitle("Grafos UI")
        self.setMinimumSize(1024, 720)
        self.resize(1400, 860)
        self.setStyleSheet(APP_STYLESHEET)
        self._build_ui()
        self._generate_graph()

    def _build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.setCentralWidget(scroll)

        central = QWidget()
        central.setObjectName("rootWidget")
        scroll.setWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.setSpacing(16)

        title_column = QVBoxLayout()
        title_column.setSpacing(4)
        title = QLabel("GRAFOS // UI")
        title.setObjectName("appTitle")
        subtitle = QLabel("RETÍCULA N×N · BFS · DFS · DIJKSTRA · RANDOM WALK")
        subtitle.setObjectName("appSubtitle")
        title_column.addWidget(title)
        title_column.addWidget(subtitle)
        header.addLayout(title_column, stretch=1)

        header_chips = QHBoxLayout()
        header_chips.setSpacing(10)
        self.mode_chip = QLabel("4 ALGORITMOS / 1 TIMER")
        self.mode_chip.setObjectName("headerChip")
        header_chips.addWidget(self.mode_chip)

        self.hardware_badge = QLabel(self.device_info.label.upper())
        self.hardware_badge.setObjectName("badge")
        header_chips.addWidget(self.hardware_badge)
        header.addLayout(header_chips)
        root.addLayout(header)

        controls_card = PanelFrame()
        controls_layout = QVBoxLayout(controls_card)
        controls_layout.setContentsMargins(18, 18, 18, 18)
        controls_layout.setSpacing(10)

        controls_row = QHBoxLayout()
        controls_row.setSpacing(12)

        self.size_input = QSpinBox()
        self.size_input.setRange(1, 100)
        self.size_input.setValue(14)

        self.density_input = QDoubleSpinBox()
        self.density_input.setRange(0.0, 1.0)
        self.density_input.setDecimals(3)
        self.density_input.setSingleStep(0.05)
        self.density_input.setValue(0.55)

        self.speed_input = QSpinBox()
        self.speed_input.setRange(30, 1500)
        self.speed_input.setSingleStep(10)
        self.speed_input.setSuffix(" ms")
        self.speed_input.setValue(140)

        form_row = QHBoxLayout()
        form_row.setSpacing(12)
        form_row.addWidget(self._field("N", self.size_input))
        form_row.addWidget(self._field("D", self.density_input))
        form_row.addWidget(self._field("Timer", self.speed_input))
        controls_row.addLayout(form_row, stretch=1)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self.generate_button = QPushButton("Generar")
        self.generate_button.setObjectName("primaryButton")
        self.generate_button.clicked.connect(self._generate_graph)
        actions_row.addWidget(self.generate_button)

        self.toggle_button = QPushButton("Iniciar")
        self.toggle_button.clicked.connect(self._toggle_simulation)
        actions_row.addWidget(self.toggle_button)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._reset_simulation)
        actions_row.addWidget(self.reset_button)

        controls_row.addLayout(actions_row)

        controls_layout.addLayout(controls_row)

        info_row = QHBoxLayout()
        info_row.setSpacing(10)

        self.density_feedback = QLabel("-")
        self.density_feedback.setObjectName("infoPill")
        self.density_feedback.setWordWrap(True)
        info_row.addWidget(self.density_feedback, stretch=2)

        self.device_detail = QLabel(self.device_info.detail)
        self.device_detail.setObjectName("infoPill")
        self.device_detail.setWordWrap(True)
        info_row.addWidget(self.device_detail, stretch=1)

        self.route_hint = QLabel("ORIGEN FIJO: (0,0) · META FIJA: (N-1,N-1)")
        self.route_hint.setObjectName("infoPill")
        info_row.addWidget(self.route_hint, stretch=1)

        controls_layout.addLayout(info_row)

        root.addWidget(controls_card)

        panels_grid = QGridLayout()
        panels_grid.setHorizontalSpacing(14)
        panels_grid.setVerticalSpacing(14)

        for index, key in enumerate(self.algorithm_order):
            panel = AlgorithmPanel(self.algorithm_styles[key])
            self.panels[key] = panel
            row, col = divmod(index, 2)
            panels_grid.addWidget(panel, row, col)
            panels_grid.setRowStretch(row, 1)
            panels_grid.setColumnStretch(col, 1)

        root.addLayout(panels_grid, stretch=1)

    def _field(self, label_text: str, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        label = QLabel(label_text.upper())
        label.setObjectName("mutedLabel")
        layout.addWidget(label)
        layout.addWidget(widget)
        return container

    def _generate_graph(self) -> None:
        config = GraphConfig(
            size=self.size_input.value(),
            density=self.density_input.value(),
            tick_ms=self.speed_input.value(),
        )
        self.timer.stop()
        self.toggle_button.setText("Iniciar")
        self.controller.generate_graph(config)
        self.timer.setInterval(config.tick_ms)
        if self.controller.metadata and self.controller.metadata.was_clamped:
            self.density_input.setValue(round(self.controller.metadata.applied_density, 3))
        self._update_density_feedback()
        self._refresh_panels()

    def _toggle_simulation(self) -> None:
        if self.controller.graph is None:
            return
        if self.controller.running:
            self.controller.pause()
            self.timer.stop()
            self.toggle_button.setText("Iniciar")
            return

        self.timer.setInterval(self.speed_input.value())
        self.controller.start()
        self.timer.start()
        self.toggle_button.setText("Pausar")

    def _reset_simulation(self) -> None:
        self.timer.stop()
        self.toggle_button.setText("Iniciar")
        self.controller.reset()
        self._refresh_panels()

    def _on_tick(self) -> None:
        if not self.controller.running:
            self.timer.stop()
            return
        snapshots = self.controller.step_all()
        self._refresh_panels(snapshots)
        if not self.controller.running:
            self.timer.stop()
            self.toggle_button.setText("Iniciar")

    def _update_density_feedback(self) -> None:
        metadata = self.controller.metadata
        if metadata is None:
            self.density_feedback.setText("-")
            return
        if metadata.was_clamped:
            self.density_feedback.setText(
                f"{metadata.display_text} | CLAMP AUTOMATICO AL MINIMO CONECTADO"
            )
        else:
            self.density_feedback.setText(metadata.display_text)

    def _refresh_panels(self, snapshots: dict[str, object] | None = None) -> None:
        graph = self.controller.graph
        current_snapshots = snapshots or self.controller.snapshots()
        for key in self.algorithm_order:
            panel = self.panels[key]
            panel.set_snapshot(graph, current_snapshots.get(key))
