#include "grafos_cpp/main_window.hpp"

#include <cmath>

#include <QFrame>
#include <QGridLayout>
#include <QHBoxLayout>
#include <QScrollArea>
#include <QVBoxLayout>

#include "grafos_cpp/styles.hpp"

namespace grafos {

MainWindow::MainWindow(QWidget* parent)
    : QMainWindow(parent),
      device_info_(detect_compute_device()),
      algorithm_styles_(build_algorithm_styles()) {
    timer_ = new QTimer(this);
    connect(timer_, &QTimer::timeout, this, &MainWindow::on_tick);

    setWindowTitle("Grafos UI");
    setMinimumSize(1024, 720);
    resize(1400, 860);
    setStyleSheet(app_stylesheet());
    build_ui();
    generate_graph();
}

int MainWindow::algorithm_panel_count() const {
    return static_cast<int>(panels_.size());
}

bool MainWindow::has_graph() const {
    return controller_.graph() != nullptr;
}

bool MainWindow::is_running() const {
    return controller_.running();
}

std::map<std::string, SearchSnapshot> MainWindow::current_snapshots() const {
    return controller_.snapshots();
}

QWidget* MainWindow::build_field(const QString& label_text, QWidget* widget) {
    auto* container = new QWidget(this);
    auto* layout = new QVBoxLayout(container);
    layout->setContentsMargins(0, 0, 0, 0);
    layout->setSpacing(6);

    auto* label = new QLabel(label_text.toUpper(), container);
    label->setObjectName("mutedLabel");
    layout->addWidget(label);
    layout->addWidget(widget);
    return container;
}

void MainWindow::build_ui() {
    auto* scroll = new QScrollArea(this);
    scroll->setWidgetResizable(true);
    scroll->setFrameShape(QFrame::NoFrame);
    setCentralWidget(scroll);

    auto* central = new QWidget(scroll);
    central->setObjectName("rootWidget");
    scroll->setWidget(central);

    auto* root = new QVBoxLayout(central);
    root->setContentsMargins(24, 24, 24, 24);
    root->setSpacing(16);

    auto* header = new QHBoxLayout();
    header->setSpacing(16);

    auto* title_column = new QVBoxLayout();
    title_column->setSpacing(4);
    auto* title = new QLabel("GRAFOS // UI", central);
    title->setObjectName("appTitle");
    auto* subtitle = new QLabel("RETICULA N×N · BFS · DFS · DIJKSTRA · RANDOM WALK", central);
    subtitle->setObjectName("appSubtitle");
    title_column->addWidget(title);
    title_column->addWidget(subtitle);
    header->addLayout(title_column, 1);

    auto* header_chips = new QHBoxLayout();
    header_chips->setSpacing(10);
    mode_chip_ = new QLabel("4 ALGORITMOS / 1 TIMER", central);
    mode_chip_->setObjectName("headerChip");
    header_chips->addWidget(mode_chip_);

    hardware_badge_ = new QLabel(QString::fromStdString(device_info_.label).toUpper(), central);
    hardware_badge_->setObjectName("badge");
    header_chips->addWidget(hardware_badge_);
    header->addLayout(header_chips);
    root->addLayout(header);

    auto* controls_card = new PanelFrame(central);
    auto* controls_layout = new QVBoxLayout(controls_card);
    controls_layout->setContentsMargins(18, 18, 18, 18);
    controls_layout->setSpacing(10);

    auto* controls_row = new QHBoxLayout();
    controls_row->setSpacing(12);

    size_input_ = new QSpinBox(controls_card);
    size_input_->setObjectName("sizeInput");
    size_input_->setRange(1, 100);
    size_input_->setValue(14);

    density_input_ = new QDoubleSpinBox(controls_card);
    density_input_->setObjectName("densityInput");
    density_input_->setRange(0.0, 1.0);
    density_input_->setDecimals(3);
    density_input_->setSingleStep(0.05);
    density_input_->setValue(0.55);

    speed_input_ = new QSpinBox(controls_card);
    speed_input_->setObjectName("speedInput");
    speed_input_->setRange(30, 1500);
    speed_input_->setSingleStep(10);
    speed_input_->setSuffix(" ms");
    speed_input_->setValue(140);

    auto* form_row = new QHBoxLayout();
    form_row->setSpacing(12);
    form_row->addWidget(build_field("N", size_input_));
    form_row->addWidget(build_field("D", density_input_));
    form_row->addWidget(build_field("Timer", speed_input_));
    controls_row->addLayout(form_row, 1);

    auto* actions_row = new QHBoxLayout();
    actions_row->setSpacing(12);

    generate_button_ = new QPushButton("Generar", controls_card);
    generate_button_->setObjectName("primaryButton");
    generate_button_->setProperty("testid", "generateButton");
    generate_button_->setAccessibleName("generateButton");
    connect(generate_button_, &QPushButton::clicked, this, &MainWindow::generate_graph);
    actions_row->addWidget(generate_button_);

    toggle_button_ = new QPushButton("Iniciar", controls_card);
    toggle_button_->setProperty("testid", "toggleButton");
    toggle_button_->setAccessibleName("toggleButton");
    connect(toggle_button_, &QPushButton::clicked, this, &MainWindow::toggle_simulation);
    actions_row->addWidget(toggle_button_);

    reset_button_ = new QPushButton("Reset", controls_card);
    reset_button_->setProperty("testid", "resetButton");
    reset_button_->setAccessibleName("resetButton");
    connect(reset_button_, &QPushButton::clicked, this, &MainWindow::reset_simulation);
    actions_row->addWidget(reset_button_);

    controls_row->addLayout(actions_row);
    controls_layout->addLayout(controls_row);

    auto* info_row = new QHBoxLayout();
    info_row->setSpacing(10);

    density_feedback_ = new QLabel("-", controls_card);
    density_feedback_->setObjectName("infoPill");
    density_feedback_->setWordWrap(true);
    info_row->addWidget(density_feedback_, 2);

    device_detail_ = new QLabel(QString::fromStdString(device_info_.detail), controls_card);
    device_detail_->setObjectName("infoPill");
    device_detail_->setWordWrap(true);
    info_row->addWidget(device_detail_, 1);

    route_hint_ = new QLabel("ORIGEN FIJO: (0,0) · META FIJA: (N-1,N-1)", controls_card);
    route_hint_->setObjectName("infoPill");
    info_row->addWidget(route_hint_, 1);

    controls_layout->addLayout(info_row);
    root->addWidget(controls_card);

    auto* panels_grid = new QGridLayout();
    panels_grid->setHorizontalSpacing(14);
    panels_grid->setVerticalSpacing(14);

    for (std::size_t index = 0; index < algorithm_order_.size(); ++index) {
        const auto& key = algorithm_order_[index];
        auto* panel = new AlgorithmPanel(algorithm_styles_.at(key), central);
        panel->setObjectName(QString("algorithmPanel_%1").arg(QString::fromStdString(key)));
        panels_[key] = panel;
        const int row = static_cast<int>(index / 2);
        const int col = static_cast<int>(index % 2);
        panels_grid->addWidget(panel, row, col);
        panels_grid->setRowStretch(row, 1);
        panels_grid->setColumnStretch(col, 1);
    }

    root->addLayout(panels_grid, 1);
}

void MainWindow::generate_graph() {
    const GraphConfig config(
        size_input_->value(),
        density_input_->value(),
        speed_input_->value()
    );
    timer_->stop();
    toggle_button_->setText("Iniciar");
    controller_.generate_graph(config);
    timer_->setInterval(config.tick_ms);
    if (const auto* metadata = controller_.metadata(); metadata != nullptr && metadata->was_clamped) {
        density_input_->setValue(std::round(metadata->applied_density * 1000.0) / 1000.0);
    }
    update_density_feedback();
    refresh_panels();
}

void MainWindow::toggle_simulation() {
    if (controller_.graph() == nullptr) {
        return;
    }
    if (controller_.running()) {
        controller_.pause();
        timer_->stop();
        toggle_button_->setText("Iniciar");
        return;
    }

    timer_->setInterval(speed_input_->value());
    controller_.start();
    timer_->start();
    toggle_button_->setText("Pausar");
}

void MainWindow::reset_simulation() {
    timer_->stop();
    toggle_button_->setText("Iniciar");
    controller_.reset();
    refresh_panels();
}

void MainWindow::on_tick() {
    if (!controller_.running()) {
        timer_->stop();
        return;
    }

    const auto snapshots = controller_.step_all();
    refresh_panels(snapshots);
    if (!controller_.running()) {
        timer_->stop();
        toggle_button_->setText("Iniciar");
    }
}

void MainWindow::update_density_feedback() {
    const auto* metadata = controller_.metadata();
    if (metadata == nullptr) {
        density_feedback_->setText("-");
        return;
    }
    if (metadata->was_clamped) {
        density_feedback_->setText(
            QString::fromStdString(metadata->display_text() + " | CLAMP AUTOMATICO AL MINIMO CONECTADO")
        );
        return;
    }
    density_feedback_->setText(QString::fromStdString(metadata->display_text()));
}

void MainWindow::refresh_panels(
    const std::optional<std::map<std::string, SearchSnapshot>>& snapshots
) {
    const GridGraph* graph = controller_.graph();
    const auto current_snapshots = snapshots.value_or(controller_.snapshots());
    for (const auto& key : algorithm_order_) {
        const auto it = current_snapshots.find(key);
        panels_.at(key)->set_snapshot(
            graph,
            it == current_snapshots.end() ? std::nullopt : std::optional<SearchSnapshot>(it->second)
        );
    }
}

}  // namespace grafos
