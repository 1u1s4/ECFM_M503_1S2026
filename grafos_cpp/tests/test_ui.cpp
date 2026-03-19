#include <chrono>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <thread>

#include <QApplication>
#include <QDoubleSpinBox>
#include <QPushButton>
#include <QSpinBox>

#include "grafos_cpp/main_window.hpp"

using namespace grafos;

namespace {

struct TestFailure : std::runtime_error {
    using std::runtime_error::runtime_error;
};

void expect(const bool condition, const std::string& message) {
    if (!condition) {
        throw TestFailure(message);
    }
}

template <typename Widget>
Widget* require_child(QWidget& parent, const QString& object_name) {
    auto* widget = parent.findChild<Widget*>(object_name);
    if (widget == nullptr) {
        throw TestFailure("Missing widget: " + object_name.toStdString());
    }
    return widget;
}

QPushButton* require_button(QWidget& parent, const QString& accessible_name) {
    const auto buttons = parent.findChildren<QPushButton*>();
    for (auto* button : buttons) {
        if (button->accessibleName() == accessible_name) {
            return button;
        }
    }
    throw TestFailure("Missing button: " + accessible_name.toStdString());
}

void pump_events(const std::chrono::milliseconds duration) {
    const auto deadline = std::chrono::steady_clock::now() + duration;
    while (std::chrono::steady_clock::now() < deadline) {
        QCoreApplication::processEvents(QEventLoop::AllEvents, 10);
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
}

}  // namespace

int main(int argc, char* argv[]) {
    qputenv("QT_QPA_PLATFORM", "offscreen");
    QApplication app(argc, argv);

    try {
        MainWindow window;
        window.show();
        pump_events(std::chrono::milliseconds(50));

        expect(window.algorithm_panel_count() == 4, "window should create four algorithm panels");
        expect(window.has_graph(), "window should generate an initial graph");

        auto* size_input = require_child<QSpinBox>(window, "sizeInput");
        auto* density_input = require_child<QDoubleSpinBox>(window, "densityInput");
        auto* speed_input = require_child<QSpinBox>(window, "speedInput");
        auto* generate_button = require_button(window, "generateButton");
        auto* toggle_button = require_button(window, "toggleButton");

        size_input->setValue(5);
        density_input->setValue(0.6);
        speed_input->setValue(30);
        generate_button->click();
        pump_events(std::chrono::milliseconds(50));

        const auto initial_snapshots = window.current_snapshots();
        expect(initial_snapshots.size() == 4, "generate should leave four snapshots");
        for (const auto& [_, snapshot] : initial_snapshots) {
            expect(snapshot.result.ticks == 0, "generate should reset ticks");
        }

        toggle_button->click();
        bool progressed = false;
        for (int attempt = 0; attempt < 40 && !progressed; ++attempt) {
            pump_events(std::chrono::milliseconds(25));
            for (const auto& [_, snapshot] : window.current_snapshots()) {
                if (snapshot.result.ticks > 0) {
                    progressed = true;
                    break;
                }
            }
        }
        expect(progressed, "timer should advance snapshots after starting simulation");
        if (window.is_running()) {
            toggle_button->click();
            pump_events(std::chrono::milliseconds(20));
        }

        size_input->setValue(1);
        density_input->setValue(1.0);
        speed_input->setValue(30);
        generate_button->click();
        pump_events(std::chrono::milliseconds(20));
        toggle_button->click();

        bool stopped = false;
        for (int attempt = 0; attempt < 20; ++attempt) {
            pump_events(std::chrono::milliseconds(20));
            if (!window.is_running()) {
                stopped = true;
                break;
            }
        }
        expect(stopped, "timer should stop when all steppers are already finished");

        std::cout << "[PASS] ui_smoke_tests\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << "[FAIL] ui_smoke_tests: " << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
