#pragma once

#include <map>
#include <optional>
#include <string>

#include <QPointF>
#include <QPainter>
#include <QFrame>
#include <QLabel>
#include <QWidget>

#include "grafos_cpp/domain.hpp"

namespace grafos {

struct AlgorithmCanvasStyle {
    std::string label;
    std::string title;
    Qt::BrushStyle visited_pattern{};
    Qt::BrushStyle frontier_pattern{};
    Qt::PenStyle path_pen_style{};
    double path_pen_width{};
};

std::map<std::string, AlgorithmCanvasStyle> build_algorithm_styles();

class PanelFrame : public QFrame {
public:
    explicit PanelFrame(QWidget* parent = nullptr);
};

class GraphCanvas : public QWidget {
public:
    explicit GraphCanvas(const AlgorithmCanvasStyle& style, QWidget* parent = nullptr);

    void set_state(const GridGraph* graph, const std::optional<SearchSnapshot>& snapshot);

protected:
    void paintEvent(QPaintEvent* event) override;

private:
    QPointF cell_center(
        const Position& position,
        double origin_x,
        double origin_y,
        double cell_size
    ) const;
    void draw_current_marker(
        QPainter& painter,
        const Position& position,
        double origin_x,
        double origin_y,
        double cell_size
    ) const;
    void draw_grid_axes(
        QPainter& painter,
        const GridGraph& graph,
        double origin_x,
        double origin_y,
        double cell_size
    ) const;

    AlgorithmCanvasStyle style_;
    const GridGraph* graph_{nullptr};
    std::optional<SearchSnapshot> snapshot_;
};

class AlgorithmPanel : public PanelFrame {
public:
    explicit AlgorithmPanel(const AlgorithmCanvasStyle& style, QWidget* parent = nullptr);

    void set_snapshot(const GridGraph* graph, const std::optional<SearchSnapshot>& snapshot);
    QString status_text() const;
    QString metric_value(const std::string& key) const;

private:
    void build_ui();

    AlgorithmCanvasStyle style_;
    QLabel* status_badge_{nullptr};
    GraphCanvas* canvas_{nullptr};
    std::map<std::string, QLabel*> metric_labels_;
};

}  // namespace grafos
