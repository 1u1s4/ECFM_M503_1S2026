#pragma once

#include <array>
#include <map>
#include <optional>
#include <string>

#include <QDoubleSpinBox>
#include <QLabel>
#include <QMainWindow>
#include <QPushButton>
#include <QSpinBox>
#include <QTimer>

#include "grafos_cpp/controller.hpp"
#include "grafos_cpp/device_detection.hpp"
#include "grafos_cpp/widgets.hpp"

namespace grafos {

class MainWindow : public QMainWindow {
public:
    explicit MainWindow(QWidget* parent = nullptr);

    int algorithm_panel_count() const;
    bool has_graph() const;
    bool is_running() const;
    std::map<std::string, SearchSnapshot> current_snapshots() const;

private:
    QWidget* build_field(const QString& label_text, QWidget* widget);
    void build_ui();
    void generate_graph();
    void toggle_simulation();
    void reset_simulation();
    void on_tick();
    void update_density_feedback();
    void refresh_panels(const std::optional<std::map<std::string, SearchSnapshot>>& snapshots = std::nullopt);

    SimulationController controller_;
    DeviceInfo device_info_;
    std::map<std::string, AlgorithmCanvasStyle> algorithm_styles_;
    std::array<std::string, 4> algorithm_order_{{"bfs", "dfs", "dijkstra", "random"}};
    std::map<std::string, AlgorithmPanel*> panels_;
    QTimer* timer_{nullptr};
    QLabel* mode_chip_{nullptr};
    QLabel* hardware_badge_{nullptr};
    QSpinBox* size_input_{nullptr};
    QDoubleSpinBox* density_input_{nullptr};
    QSpinBox* speed_input_{nullptr};
    QPushButton* generate_button_{nullptr};
    QPushButton* toggle_button_{nullptr};
    QPushButton* reset_button_{nullptr};
    QLabel* density_feedback_{nullptr};
    QLabel* device_detail_{nullptr};
    QLabel* route_hint_{nullptr};
};

}  // namespace grafos
