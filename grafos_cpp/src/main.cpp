#include <QApplication>

#include "grafos_cpp/main_window.hpp"

int main(int argc, char* argv[]) {
    QApplication app(argc, argv);
    app.setApplicationName("Grafos UI");

    grafos::MainWindow window;
    window.show();
    return app.exec();
}
