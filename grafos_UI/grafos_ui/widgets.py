from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from .domain import GridGraph, SearchSnapshot


@dataclass(frozen=True, slots=True)
class AlgorithmCanvasStyle:
    label: str
    title: str
    visited_pattern: Qt.BrushStyle
    frontier_pattern: Qt.BrushStyle
    path_pen_style: Qt.PenStyle
    path_pen_width: float


def build_algorithm_styles() -> dict[str, AlgorithmCanvasStyle]:
    return {
        "bfs": AlgorithmCanvasStyle(
            label="BFS",
            title="BUSQUEDA EN AMPLITUD",
            visited_pattern=Qt.BrushStyle.Dense4Pattern,
            frontier_pattern=Qt.BrushStyle.HorPattern,
            path_pen_style=Qt.PenStyle.SolidLine,
            path_pen_width=3.5,
        ),
        "dfs": AlgorithmCanvasStyle(
            label="DFS",
            title="BUSQUEDA EN PROFUNDIDAD",
            visited_pattern=Qt.BrushStyle.BDiagPattern,
            frontier_pattern=Qt.BrushStyle.Dense6Pattern,
            path_pen_style=Qt.PenStyle.DashLine,
            path_pen_width=3.0,
        ),
        "dijkstra": AlgorithmCanvasStyle(
            label="DIJKSTRA",
            title="COSTO MINIMO",
            visited_pattern=Qt.BrushStyle.CrossPattern,
            frontier_pattern=Qt.BrushStyle.Dense2Pattern,
            path_pen_style=Qt.PenStyle.SolidLine,
            path_pen_width=4.5,
        ),
        "random": AlgorithmCanvasStyle(
            label="RANDOM",
            title="RANDOM WALK",
            visited_pattern=Qt.BrushStyle.FDiagPattern,
            frontier_pattern=Qt.BrushStyle.VerPattern,
            path_pen_style=Qt.PenStyle.DotLine,
            path_pen_width=3.0,
        ),
    }


class PanelFrame(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("panelFrame")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(0)
        shadow.setOffset(6, 6)
        shadow.setColor(QColor(0, 0, 0))
        self.setGraphicsEffect(shadow)


class GraphCanvas(QWidget):
    def __init__(self, style: AlgorithmCanvasStyle, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._style = style
        self._graph: GridGraph | None = None
        self._snapshot: SearchSnapshot | None = None
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(180, 180)

    def set_state(self, graph: GridGraph | None, snapshot: SearchSnapshot | None) -> None:
        self._graph = graph
        self._snapshot = snapshot
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        if self._graph is None or self._snapshot is None:
            painter.setPen(QPen(Qt.GlobalColor.black, 1))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Genera un grafo")
            return

        graph = self._graph
        snapshot = self._snapshot
        visited = set(snapshot.visited)
        frontier = set(snapshot.frontier)
        path = tuple(snapshot.path)

        padding = 12
        cell_size = min(
            (self.width() - (padding * 2)) / graph.size,
            (self.height() - (padding * 2)) / graph.size,
        )
        if cell_size <= 0:
            return

        origin_x = (self.width() - (cell_size * graph.size)) / 2
        origin_y = (self.height() - (cell_size * graph.size)) / 2

        visited_brush = QBrush(Qt.GlobalColor.black, self._style.visited_pattern)
        frontier_brush = QBrush(Qt.GlobalColor.black, self._style.frontier_pattern)
        inactive_brush = QBrush(Qt.GlobalColor.white, Qt.BrushStyle.DiagCrossPattern)
        border_pen = QPen(Qt.GlobalColor.black, max(1.2, cell_size * 0.03))
        inactive_pen = QPen(Qt.GlobalColor.black, max(0.8, cell_size * 0.025))
        path_pen = QPen(
            Qt.GlobalColor.black,
            min(self._style.path_pen_width, max(1.0, cell_size * 0.18)),
            self._style.path_pen_style,
        )
        inner_inset = min(max(0.5, cell_size * 0.05), max(0.5, cell_size / 5))
        frontier_inset = min(max(0.75, cell_size * 0.12), max(0.75, cell_size / 3.2))
        path_inset = min(max(0.75, cell_size * 0.08), max(0.75, cell_size / 4))

        for row in range(graph.size):
            for col in range(graph.size):
                position = (row, col)
                vertex = graph.vertex_at(position)
                rect = QRectF(
                    origin_x + (col * cell_size),
                    origin_y + (row * cell_size),
                    cell_size,
                    cell_size,
                )

                painter.fillRect(rect, Qt.GlobalColor.white)
                if not vertex.active:
                    painter.fillRect(rect, inactive_brush)
                    painter.setPen(inactive_pen)
                    painter.drawLine(rect.topLeft(), rect.bottomRight())
                    painter.drawLine(rect.topRight(), rect.bottomLeft())
                else:
                    inner = rect.adjusted(inner_inset, inner_inset, -inner_inset, -inner_inset)
                    if position in visited:
                        painter.fillRect(inner, visited_brush)
                    if position in frontier:
                        painter.fillRect(
                            inner.adjusted(
                                frontier_inset,
                                frontier_inset,
                                -frontier_inset,
                                -frontier_inset,
                            ),
                            frontier_brush,
                        )

                painter.setPen(border_pen)
                painter.drawRect(rect)

                if vertex.active and graph.size <= 8 and cell_size >= 44:
                    painter.setPen(
                        QPen(
                            Qt.GlobalColor.white
                            if position == snapshot.current
                            else Qt.GlobalColor.black
                        )
                    )
                    font = QFont("Space Mono", max(7, int(cell_size * 0.18)))
                    painter.setFont(font)
                    painter.drawText(
                        rect.adjusted(4, 8, -4, -4),
                        Qt.AlignmentFlag.AlignCenter,
                        f"{vertex.weight:.2f}",
                    )

                if cell_size >= 22 and position in {graph.start, graph.goal}:
                    painter.setPen(
                        QPen(
                            Qt.GlobalColor.white
                            if position == snapshot.current or not vertex.active
                            else Qt.GlobalColor.black
                        )
                    )
                    font = QFont("Space Mono", max(8, int(cell_size * 0.22)))
                    font.setBold(True)
                    painter.setFont(font)
                    marker = "S" if position == graph.start else "G"
                    painter.drawText(
                        rect.adjusted(4, 2, -4, -2),
                        Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
                        marker,
                    )

        if len(path) >= 2:
            painter.setPen(path_pen)
            for left, right in zip(path, path[1:]):
                left_center = self._cell_center(left, origin_x, origin_y, cell_size)
                right_center = self._cell_center(right, origin_x, origin_y, cell_size)
                painter.drawLine(left_center, right_center)

        if snapshot.current is not None:
            self._draw_current_marker(painter, snapshot.current, origin_x, origin_y, cell_size)

        self._draw_grid_axes(painter, graph, origin_x, origin_y, cell_size)

    def _cell_center(
        self,
        position: tuple[int, int],
        origin_x: float,
        origin_y: float,
        cell_size: float,
    ):
        row, col = position
        return (
            rect_center := QRectF(
                origin_x + (col * cell_size),
                origin_y + (row * cell_size),
                cell_size,
                cell_size,
            ).center()
        )

    def _draw_current_marker(
        self,
        painter: QPainter,
        position: tuple[int, int],
        origin_x: float,
        origin_y: float,
        cell_size: float,
    ) -> None:
        center = self._cell_center(position, origin_x, origin_y, cell_size)
        radius = max(4.0, min(cell_size * 0.16, 12.0))
        painter.setPen(QPen(Qt.GlobalColor.white, max(1.5, radius * 0.25)))
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawEllipse(center, radius, radius)

    def _draw_grid_axes(
        self,
        painter: QPainter,
        graph: GridGraph,
        origin_x: float,
        origin_y: float,
        cell_size: float,
    ) -> None:
        if graph.size > 6:
            return
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        font = QFont("Space Mono", max(8, int(cell_size * 0.2)))
        painter.setFont(font)
        for index in range(graph.size):
            x = origin_x + (index * cell_size) + (cell_size / 2)
            y = origin_y + (index * cell_size) + (cell_size / 2)
            painter.drawText(
                QRectF(x - 12, origin_y - 18, 24, 16),
                Qt.AlignmentFlag.AlignCenter,
                str(index),
            )
            painter.drawText(
                QRectF(origin_x - 18, y - 8, 16, 16),
                Qt.AlignmentFlag.AlignCenter,
                str(index),
            )


class AlgorithmPanel(PanelFrame):
    def __init__(self, style: AlgorithmCanvasStyle, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._style = style
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        title_stack = QVBoxLayout()
        title_stack.setSpacing(2)

        self.title_label = QLabel(self._style.label)
        self.title_label.setObjectName("panelTitle")
        title_stack.addWidget(self.title_label)

        self.subtitle_label = QLabel(self._style.title)
        self.subtitle_label.setObjectName("panelSubtitle")
        title_stack.addWidget(self.subtitle_label)
        header_row.addLayout(title_stack, stretch=1)

        self.status_badge = QLabel("LISTO")
        self.status_badge.setObjectName("statusBadge")
        header_row.addWidget(self.status_badge, alignment=Qt.AlignmentFlag.AlignTop)
        layout.addLayout(header_row)

        self.metric_labels: dict[str, QLabel] = {}
        labels = [
            "Ticks",
            "Visitados",
            "Frontera",
            "Camino",
            "Costo",
            "Extra",
        ]
        self.canvas = GraphCanvas(self._style)
        layout.addWidget(self.canvas, stretch=1)

        metrics_grid = QGridLayout()
        metrics_grid.setHorizontalSpacing(10)
        metrics_grid.setVerticalSpacing(10)

        for index, label in enumerate(labels):
            card = QFrame()
            card.setObjectName("metricCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(2)
            name_label = QLabel(label.upper())
            name_label.setObjectName("metricKey")
            value_label = QLabel("-")
            value_label.setObjectName("metricValue")
            value_label.setWordWrap(True)
            card_layout.addWidget(name_label)
            card_layout.addWidget(value_label)
            row, col = divmod(index, 3)
            metrics_grid.addWidget(card, row, col)
            self.metric_labels[label] = value_label

        layout.addLayout(metrics_grid)

    def set_snapshot(self, graph: GridGraph | None, snapshot: SearchSnapshot | None) -> None:
        self.canvas.set_state(graph, snapshot)
        if snapshot is None:
            self.status_badge.setText("LISTO")
            for label in self.metric_labels.values():
                label.setText("-")
            return

        result = snapshot.result
        self.status_badge.setText(snapshot.status.upper())
        self.metric_labels["Ticks"].setText(str(result.ticks))
        self.metric_labels["Visitados"].setText(str(result.visited_count))
        self.metric_labels["Frontera"].setText(str(result.frontier_size))
        self.metric_labels["Camino"].setText(f"{result.path_nodes} nodos / {result.path_edges} aristas")
        self.metric_labels["Costo"].setText(
            "-" if result.total_cost is None else f"{result.total_cost:.3f}"
        )
        if snapshot.metadata:
            self.metric_labels["Extra"].setText(
                " | ".join(f"{key}: {value}" for key, value in snapshot.metadata.items())
            )
        else:
            self.metric_labels["Extra"].setText("-")
