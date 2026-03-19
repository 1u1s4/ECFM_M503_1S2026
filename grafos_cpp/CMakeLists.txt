cmake_minimum_required(VERSION 3.21)

project(grafos_ui_cpp LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_AUTOMOC OFF)
set(CMAKE_AUTOUIC OFF)
set(CMAKE_AUTORCC OFF)

include(CTest)

add_library(grafos_core
    src/domain.cpp
    src/generator.cpp
    src/algorithms.cpp
    src/controller.cpp
    src/device_detection.cpp
)

target_include_directories(grafos_core
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_compile_features(grafos_core PUBLIC cxx_std_20)

find_package(Qt6 COMPONENTS Widgets QUIET)

if(Qt6_FOUND)
    set(CMAKE_AUTOMOC ON)

    add_library(grafos_ui
        src/styles.cpp
        src/widgets.cpp
        src/main_window.cpp
    )

    target_include_directories(grafos_ui
        PUBLIC
            ${CMAKE_CURRENT_SOURCE_DIR}/include
    )

    target_link_libraries(grafos_ui
        PUBLIC
            grafos_core
            Qt6::Widgets
    )

    add_executable(grafos_ui_cpp src/main.cpp)
    target_link_libraries(grafos_ui_cpp PRIVATE grafos_ui)
else()
    message(WARNING "Qt6 Widgets no esta disponible; se omite la build de UI y solo se habilita el nucleo C++.")
endif()

if(BUILD_TESTING)
    add_executable(graph_core_tests
        tests/test_core.cpp
    )
    target_link_libraries(graph_core_tests PRIVATE grafos_core)
    target_compile_definitions(graph_core_tests PRIVATE GRAFOS_CPP_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
    add_test(NAME graph_core_tests COMMAND graph_core_tests)

    if(Qt6_FOUND)
        add_executable(ui_smoke_tests
            tests/test_ui.cpp
        )
        target_link_libraries(ui_smoke_tests PRIVATE grafos_ui)
        target_compile_definitions(ui_smoke_tests PRIVATE GRAFOS_CPP_SOURCE_DIR="${CMAKE_CURRENT_SOURCE_DIR}")
        add_test(NAME ui_smoke_tests COMMAND ui_smoke_tests)
        set_tests_properties(ui_smoke_tests PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen")
    endif()
endif()
