#include "grafos_cpp/widgets.hpp"

#include <algorithm>
#include <cmath>

#include <QBrush>
#include <QFont>
#include <QGraphicsDropShadowEffect>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QPainter>
#include <QPaintEvent>
#include <QPen>
#include <QRectF>
#include <QSizePolicy>
#include <QStringList>
#include <QVBoxLayout>

namespace grafos {

std::map<std::string, AlgorithmCanvasStyle> build_algorithm_styles() {
    return {
        {"bfs", AlgorithmCanvasStyle{"BFS", "BUSQUEDA EN AMPLITUD", Qt::Dense4Pattern, Qt::HorPattern, Qt::SolidLine, 3.5}},
        {"dfs", AlgorithmCanvasStyle{"DFS", "BUSQUEDA EN PROFUNDIDAD", Qt::BDiagPattern, Qt::Dense6Pattern, Qt::DashLine, 3.0}},
        {"dijkstra", AlgorithmCanvasStyle{"DIJKSTRA", "COSTO MINIMO", Qt::CrossPattern, Qt::Dense2Pattern, Qt::SolidLine, 4.5}},
        {"random", AlgorithmCanvasStyle{"RANDOM", "RANDOM WALK", Qt::FDiagPattern, Qt::VerPattern, Qt::DotLine, 3.0}},
    };
}

PanelFrame::PanelFrame(QWidget* parent) : QFrame(parent) {
    setObjectName("panelFrame");
    auto* shadow = new QGraphicsDropShadowEffect(this);
    shadow->setBlurRadius(0);
    shadow->setOffset(6, 6);
    shadow->setColor(QColor(0, 0, 0));
    setGraphicsEffect(shadow);
}

GraphCanvas::GraphCanvas(const AlgorithmCanvasStyle& style, QWidget* parent)
    : QWidget(parent), style_(style) {
    setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    setMinimumSize(180, 180);
}

void GraphCanvas::set_state(const GridGraph* graph, const std::optional<SearchSnapshot>& snapshot) {
    graph_ = graph;
    snapshot_ = snapshot;
    update();
}

void GraphCanvas::paintEvent(QPaintEvent* event) {
    QWidget::paintEvent(event);

    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing, true);
    painter.fillRect(rect(), Qt::white);

    if (graph_ == nullptr || !snapshot_.has_value()) {
        painter.setPen(QPen(Qt::black, 1));
        painter.drawText(rect(), Qt::AlignCenter, "Genera un grafo");
        return;
    }

    const auto& graph = *graph_;
    const auto& snapshot = *snapshot_;
    const std::set<Position> visited(snapshot.visited.begin(), snapshot.visited.end());
    const std::set<Position> frontier(snapshot.frontier.begin(), snapshot.frontier.end());
    const auto& path = snapshot.path;

    const double padding = 12.0;
    const double cell_size = std::min(
        (width() - (padding * 2.0)) / static_cast<double>(graph.size),
        (height() - (padding * 2.0)) / static_cast<double>(graph.size)
    );
    if (cell_size <= 0.0) {
        return;
    }

    const double origin_x = (width() - (cell_size * graph.size)) / 2.0;
    const double origin_y = (height() - (cell_size * graph.size)) / 2.0;

    const QBrush visited_brush(Qt::black, style_.visited_pattern);
    const QBrush frontier_brush(Qt::black, style_.frontier_pattern);
    const QBrush inactive_brush(Qt::white, Qt::DiagCrossPattern);
    const QPen border_pen(Qt::black, std::max(1.2, cell_size * 0.03));
    const QPen inactive_pen(Qt::black, std::max(0.8, cell_size * 0.025));
    const QPen path_pen(
        Qt::black,
        std::min(style_.path_pen_width, std::max(1.0, cell_size * 0.18)),
        style_.path_pen_style
    );
    const double inner_inset = std::min(std::max(0.5, cell_size * 0.05), std::max(0.5, cell_size / 5.0));
    const double frontier_inset = std::min(std::max(0.75, cell_size * 0.12), std::max(0.75, cell_size / 3.2));

    for (int row = 0; row < graph.size; ++row) {
        for (int col = 0; col < graph.size; ++col) {
            const Position position{row, col};
            const auto& vertex = graph.vertex_at(position);
            const QRectF cell_rect(
                origin_x + (static_cast<double>(col) * cell_size),
                origin_y + (static_cast<double>(row) * cell_size),
                cell_size,
                cell_size
            );

            painter.fillRect(cell_rect, Qt::white);
            if (!vertex.active) {
                painter.fillRect(cell_rect, inactive_brush);
                painter.setPen(inactive_pen);
                painter.drawLine(cell_rect.topLeft(), cell_rect.bottomRight());
                painter.drawLine(cell_rect.topRight(), cell_rect.bottomLeft());
            } else {
                const QRectF inner = cell_rect.adjusted(inner_inset, inner_inset, -inner_inset, -inner_inset);
                if (visited.contains(position)) {
                    painter.fillRect(inner, visited_brush);
                }
                if (frontier.contains(position)) {
                    painter.fillRect(
                        inner.adjusted(frontier_inset, frontier_inset, -frontier_inset, -frontier_inset),
                        frontier_brush
                    );
                }
            }

            painter.setPen(border_pen);
            painter.drawRect(cell_rect);

            if (vertex.active && graph.size <= 8 && cell_size >= 44.0) {
                painter.setPen(
                    QPen(
                        snapshot.current.has_value() && snapshot.current.value() == position
                            ? Qt::white
                            : Qt::black
                    )
                );
                QFont font("Space Mono", std::max(7, static_cast<int>(cell_size * 0.18)));
                painter.setFont(font);
                painter.drawText(
                    cell_rect.adjusted(4.0, 8.0, -4.0, -4.0),
                    Qt::AlignCenter,
                    QString::number(vertex.weight, 'f', 2)
                );
            }

            if (cell_size >= 22.0 && (position == graph.start || position == graph.goal)) {
                painter.setPen(
                    QPen(
                        ((!vertex.active) || (snapshot.current.has_value() && snapshot.current.value() == position))
                            ? Qt::white
                            : Qt::black
                    )
                );
                QFont font("Space Mono", std::max(8, static_cast<int>(cell_size * 0.22)));
                font.setBold(true);
                painter.setFont(font);
                painter.drawText(
                    cell_rect.adjusted(4.0, 2.0, -4.0, -2.0),
                    Qt::AlignTop | Qt::AlignLeft,
                    position == graph.start ? "S" : "G"
                );
            }
        }
    }

    if (path.size() >= 2) {
        painter.setPen(path_pen);
        for (std::size_t index = 0; index + 1 < path.size(); ++index) {
            painter.drawLine(
                cell_center(path[index], origin_x, origin_y, cell_size),
                cell_center(path[index + 1], origin_x, origin_y, cell_size)
            );
        }
    }

    if (snapshot.current.has_value()) {
        draw_current_marker(painter, *snapshot.current, origin_x, origin_y, cell_size);
    }

    draw_grid_axes(painter, graph, origin_x, origin_y, cell_size);
}

QPointF GraphCanvas::cell_center(
    const Position& position,
    const double origin_x,
    const double origin_y,
    const double cell_size
) const {
    const QRectF cell_rect(
        origin_x + (static_cast<double>(position.col) * cell_size),
        origin_y + (static_cast<double>(position.row) * cell_size),
        cell_size,
        cell_size
    );
    return cell_rect.center();
}

void GraphCanvas::draw_current_marker(
    QPainter& painter,
    const Position& position,
    const double origin_x,
    const double origin_y,
    const double cell_size
) const {
    const QPointF center = cell_center(position, origin_x, origin_y, cell_size);
    const double radius = std::max(4.0, std::min(cell_size * 0.16, 12.0));
    painter.setPen(QPen(Qt::white, std::max(1.5, radius * 0.25)));
    painter.setBrush(QBrush(Qt::black));
    painter.drawEllipse(center, radius, radius);
}

void GraphCanvas::draw_grid_axes(
    QPainter& painter,
    const GridGraph& graph,
    const double origin_x,
    const double origin_y,
    const double cell_size
) const {
    if (graph.size > 6) {
        return;
    }

    painter.setPen(QPen(Qt::black, 1));
    QFont font("Space Mono", std::max(8, static_cast<int>(cell_size * 0.2)));
    painter.setFont(font);
    for (int index = 0; index < graph.size; ++index) {
        const double x = origin_x + (static_cast<double>(index) * cell_size) + (cell_size / 2.0);
        const double y = origin_y + (static_cast<double>(index) * cell_size) + (cell_size / 2.0);
        painter.drawText(QRectF(x - 12.0, origin_y - 18.0, 24.0, 16.0), Qt::AlignCenter, QString::number(index));
        painter.drawText(QRectF(origin_x - 18.0, y - 8.0, 16.0, 16.0), Qt::AlignCenter, QString::number(index));
    }
}

AlgorithmPanel::AlgorithmPanel(const AlgorithmCanvasStyle& style, QWidget* parent)
    : PanelFrame(parent), style_(style) {
    build_ui();
}

void AlgorithmPanel::set_snapshot(const GridGraph* graph, const std::optional<SearchSnapshot>& snapshot) {
    canvas_->set_state(graph, snapshot);
    if (!snapshot.has_value()) {
        status_badge_->setText("LISTO");
        for (auto& [_, label] : metric_labels_) {
            label->setText("-");
        }
        return;
    }

    const auto& result = snapshot->result;
    status_badge_->setText(QString::fromStdString(snapshot->status).toUpper());
    metric_labels_.at("Ticks")->setText(QString::number(result.ticks));
    metric_labels_.at("Visitados")->setText(QString::number(result.visited_count));
    metric_labels_.at("Frontera")->setText(QString::number(result.frontier_size));
    metric_labels_.at("Camino")->setText(
        QString("%1 nodos / %2 aristas").arg(result.path_nodes).arg(result.path_edges)
    );
    metric_labels_.at("Costo")->setText(
        result.total_cost.has_value()
            ? QString::number(*result.total_cost, 'f', 3)
            : "-"
    );

    if (snapshot->metadata.empty()) {
        metric_labels_.at("Extra")->setText("-");
        return;
    }

    QStringList parts;
    for (const auto& [key, value] : snapshot->metadata) {
        parts << QString("%1: %2").arg(QString::fromStdString(key), QString::fromStdString(value));
    }
    metric_labels_.at("Extra")->setText(parts.join(" | "));
}

QString AlgorithmPanel::status_text() const {
    return status_badge_->text();
}

QString AlgorithmPanel::metric_value(const std::string& key) const {
    const auto it = metric_labels_.find(key);
    return it == metric_labels_.end() ? QString{} : it->second->text();
}

void AlgorithmPanel::build_ui() {
    auto* layout = new QVBoxLayout(this);
    layout->setContentsMargins(16, 16, 16, 16);
    layout->setSpacing(12);

    auto* header_row = new QHBoxLayout();
    header_row->setSpacing(12);

    auto* title_stack = new QVBoxLayout();
    title_stack->setSpacing(2);

    auto* title_label = new QLabel(QString::fromStdString(style_.label), this);
    title_label->setObjectName("panelTitle");
    title_stack->addWidget(title_label);

    auto* subtitle_label = new QLabel(QString::fromStdString(style_.title), this);
    subtitle_label->setObjectName("panelSubtitle");
    title_stack->addWidget(subtitle_label);
    header_row->addLayout(title_stack, 1);

    status_badge_ = new QLabel("LISTO", this);
    status_badge_->setObjectName("statusBadge");
    header_row->addWidget(status_badge_, 0, Qt::AlignTop);
    layout->addLayout(header_row);

    canvas_ = new GraphCanvas(style_, this);
    layout->addWidget(canvas_, 1);

    auto* metrics_grid = new QGridLayout();
    metrics_grid->setHorizontalSpacing(10);
    metrics_grid->setVerticalSpacing(10);

    const std::vector<std::string> labels{"Ticks", "Visitados", "Frontera", "Camino", "Costo", "Extra"};
    for (std::size_t index = 0; index < labels.size(); ++index) {
        auto* card = new QFrame(this);
        card->setObjectName("metricCard");
        auto* card_layout = new QVBoxLayout(card);
        card_layout->setContentsMargins(10, 8, 10, 8);
        card_layout->setSpacing(2);

        auto* name_label = new QLabel(QString::fromStdString(labels[index]).toUpper(), card);
        name_label->setObjectName("metricKey");
        auto* value_label = new QLabel("-", card);
        value_label->setObjectName("metricValue");
        value_label->setWordWrap(true);
        card_layout->addWidget(name_label);
        card_layout->addWidget(value_label);

        const int row = static_cast<int>(index / 3);
        const int col = static_cast<int>(index % 3);
        metrics_grid->addWidget(card, row, col);
        metric_labels_[labels[index]] = value_label;
    }

    layout->addLayout(metrics_grid);
}

}  // namespace grafos
