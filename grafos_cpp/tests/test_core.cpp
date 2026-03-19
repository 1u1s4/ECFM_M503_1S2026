#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <functional>
#include <iostream>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "grafos_cpp/algorithms.hpp"
#include "grafos_cpp/controller.hpp"
#include "grafos_cpp/generator.hpp"

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

void expect_equal(const std::string& actual, const std::string& expected, const std::string& label) {
    if (actual != expected) {
        throw TestFailure(label + " expected [" + expected + "] but got [" + actual + "]");
    }
}

void expect_near(const double actual, const double expected, const double epsilon, const std::string& label) {
    if (std::abs(actual - expected) > epsilon) {
        std::ostringstream buffer;
        buffer << label << " expected " << expected << " but got " << actual;
        throw TestFailure(buffer.str());
    }
}

template <typename Fn>
void expect_invalid_argument(Fn&& fn, const std::string& label) {
    try {
        fn();
    } catch (const std::invalid_argument&) {
        return;
    }
    throw TestFailure(label + " did not throw std::invalid_argument");
}

void run_until_finished(SearchStepper& stepper, const int max_steps = 200) {
    for (int index = 0; index < max_steps; ++index) {
        if (stepper.is_finished()) {
            return;
        }
        stepper.step();
    }
    throw TestFailure(stepper.display_name() + " did not finish");
}

GridGraph build_manual_graph(
    const std::vector<Position>& active,
    const std::map<Position, double>& weights,
    const int size = 3
) {
    std::map<Position, Vertex> vertices;
    const std::set<Position> active_positions(active.begin(), active.end());
    for (int row = 0; row < size; ++row) {
        for (int col = 0; col < size; ++col) {
            const Position position{row, col};
            const bool is_active = active_positions.contains(position);
            const auto it = weights.find(position);
            vertices[position] = Vertex{
                row,
                col,
                is_active && it != weights.end() ? it->second : 0.0,
                is_active,
            };
        }
    }
    return GridGraph{
        size,
        vertices,
        Position{0, 0},
        Position{size - 1, size - 1},
        static_cast<double>(active.size()) / static_cast<double>(size * size),
        static_cast<int>(active.size()),
        size * size,
    };
}

std::string serialize_path(const std::vector<Position>& path) {
    std::ostringstream buffer;
    for (std::size_t index = 0; index < path.size(); ++index) {
        if (index > 0) {
            buffer << ';';
        }
        buffer << path[index].row << ',' << path[index].col;
    }
    return buffer.str();
}

std::map<std::string, std::string> run_python_scenario(const std::string& scenario) {
#ifndef GRAFOS_CPP_SOURCE_DIR
#error "GRAFOS_CPP_SOURCE_DIR must be defined"
#endif
    const std::string script_path = std::string(GRAFOS_CPP_SOURCE_DIR) + "/tests/py_reference.py";
    const std::string command = "python3 \"" + script_path + "\" " + scenario;

    FILE* pipe = popen(command.c_str(), "r");
    if (pipe == nullptr) {
        throw TestFailure("Failed to start python reference command");
    }

    std::string output;
    std::array<char, 256> buffer{};
    while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe) != nullptr) {
        output += buffer.data();
    }
    const int exit_code = pclose(pipe);
    if (exit_code != 0) {
        throw TestFailure("Python reference command failed for scenario " + scenario);
    }

    std::map<std::string, std::string> result;
    std::istringstream lines(output);
    std::string line;
    while (std::getline(lines, line)) {
        if (line.empty()) {
            continue;
        }
        const auto separator = line.find('=');
        if (separator == std::string::npos) {
            throw TestFailure("Malformed python reference output: " + line);
        }
        result[line.substr(0, separator)] = line.substr(separator + 1);
    }
    return result;
}

void test_graph_config() {
    expect_invalid_argument([] { GraphConfig(0, 0.5, 100); }, "size below range");
    expect_invalid_argument([] { GraphConfig(101, 0.5, 100); }, "size above range");
    expect_invalid_argument([] { GraphConfig(4, -0.1, 100); }, "density below range");
    expect_invalid_argument([] { GraphConfig(4, 1.1, 100); }, "density above range");
    expect_invalid_argument([] { GraphConfig(4, 0.5, 0); }, "tick non-positive");
}

void test_factory_clamp() {
    const GraphConfig config(4, 0.10, 100, 7U);
    auto build = GridGraphFactory().build(config);

    expect(build.metadata.was_clamped, "factory should clamp density");
    expect_near(build.metadata.min_density, minimum_density(4), 1e-9, "min density");
    expect(build.graph.actual_density >= build.metadata.min_density, "actual density should satisfy minimum");
    expect(build.graph.start == Position{0, 0}, "start should be origin");
    expect(build.graph.goal == Position{3, 3}, "goal should be bottom-right");

    for (const auto& position : build.graph.active_positions()) {
        expect(!build.graph.neighbors(position).empty(), "every active node should have a neighbor");
    }

    BreadthFirstStepper bfs(build.graph);
    run_until_finished(bfs);
    expect(bfs.result().found, "BFS should find a path on generated graph");
    expect(bfs.result().path.front() == build.graph.start, "BFS path should start at origin");
    expect(bfs.result().path.back() == build.graph.goal, "BFS path should end at goal");

    const auto parity = run_python_scenario("factory_clamp");
    expect_equal(build.metadata.was_clamped ? "1" : "0", parity.at("was_clamped"), "factory clamp flag");
    expect_near(build.metadata.min_density, std::stod(parity.at("min_density")), 1e-6, "factory min density parity");
    expect_near(build.graph.actual_density, std::stod(parity.at("actual_density")), 1e-6, "factory actual density parity");
    expect_equal("0,0", parity.at("start"), "factory start parity");
    expect_equal("3,3", parity.at("goal"), "factory goal parity");
    expect_equal(bfs.result().found ? "1" : "0", parity.at("bfs_found"), "factory BFS parity");
}

void test_single_vertex() {
    auto build = GridGraphFactory().build(GraphConfig(1, 1.0, 100, 1U));
    DijkstraStepper dijkstra(build.graph);

    expect(build.graph.start == build.graph.goal, "single vertex graph should have same start and goal");
    expect_near(build.graph.actual_density, 0.0, 1e-9, "single vertex graph density");
    expect_near(build.metadata.actual_density, 0.0, 1e-9, "single vertex metadata density");
    expect(dijkstra.is_finished(), "single vertex dijkstra should finish immediately");
    expect(dijkstra.result().path_nodes == 1, "single vertex path nodes");
    expect(dijkstra.result().path_edges == 0, "single vertex path edges");
    expect_near(*dijkstra.result().total_cost, 0.0, 1e-9, "single vertex total cost");

    const auto parity = run_python_scenario("single_vertex");
    expect_equal("0,0", parity.at("start"), "single vertex start parity");
    expect_equal("0,0", parity.at("goal"), "single vertex goal parity");
    expect_near(build.graph.actual_density, std::stod(parity.at("graph_density")), 1e-6, "single vertex graph density parity");
    expect_near(build.metadata.actual_density, std::stod(parity.at("metadata_density")), 1e-6, "single vertex metadata density parity");
    expect_equal(std::to_string(dijkstra.result().path_nodes), parity.at("path_nodes"), "single vertex path nodes parity");
    expect_equal(std::to_string(dijkstra.result().path_edges), parity.at("path_edges"), "single vertex path edges parity");
    expect_near(*dijkstra.result().total_cost, std::stod(parity.at("total_cost")), 1e-6, "single vertex total cost parity");
}

void test_manual_algorithms() {
    const std::vector<Position> active{
        Position{0, 0}, Position{0, 1}, Position{0, 2}, Position{1, 0},
        Position{1, 2}, Position{2, 0}, Position{2, 1}, Position{2, 2},
    };
    const std::map<Position, double> weights{
        {Position{0, 0}, 0.0},
        {Position{0, 1}, 0.9},
        {Position{0, 2}, 0.9},
        {Position{1, 0}, 0.1},
        {Position{1, 2}, 0.9},
        {Position{2, 0}, 0.1},
        {Position{2, 1}, 0.1},
        {Position{2, 2}, 0.1},
    };
    const GridGraph graph = build_manual_graph(active, weights);

    BreadthFirstStepper bfs(graph);
    DepthFirstStepper dfs(graph);
    DijkstraStepper dijkstra(graph);
    run_until_finished(bfs);
    run_until_finished(dfs);
    run_until_finished(dijkstra);

    expect(bfs.result().found, "manual BFS should find path");
    expect_equal(
        serialize_path(bfs.result().path),
        "0,0;0,1;0,2;1,2;2,2",
        "manual BFS path"
    );
    expect(bfs.result().path_edges == 4, "manual BFS edge count");

    expect(dfs.result().found, "manual DFS should find path");
    expect(dfs.result().path.front() == graph.start, "manual DFS start");
    expect(dfs.result().path.back() == graph.goal, "manual DFS end");
    for (std::size_t index = 0; index + 1 < dfs.result().path.size(); ++index) {
        const auto neighbors = graph.neighbors(dfs.result().path[index]);
        expect(
            std::find(neighbors.begin(), neighbors.end(), dfs.result().path[index + 1]) != neighbors.end(),
            "manual DFS path should follow edges"
        );
    }

    expect(dijkstra.result().found, "manual Dijkstra should find path");
    expect_equal(
        serialize_path(dijkstra.result().path),
        "0,0;1,0;2,0;2,1;2,2",
        "manual Dijkstra path"
    );
    expect_near(*dijkstra.result().total_cost, 0.4, 1e-9, "manual Dijkstra cost");

    const auto parity = run_python_scenario("manual_algorithms");
    expect_equal(serialize_path(bfs.result().path), parity.at("bfs_path"), "manual BFS parity");
    expect_equal(
        std::to_string(dfs.result().path.front().row) + "," + std::to_string(dfs.result().path.front().col),
        parity.at("dfs_start"),
        "manual DFS start parity"
    );
    expect_equal(
        std::to_string(dfs.result().path.back().row) + "," + std::to_string(dfs.result().path.back().col),
        parity.at("dfs_end"),
        "manual DFS end parity"
    );
    expect_equal(serialize_path(dijkstra.result().path), parity.at("dijkstra_path"), "manual Dijkstra parity");
    expect_near(*dijkstra.result().total_cost, std::stod(parity.at("dijkstra_cost")), 1e-6, "manual Dijkstra cost parity");
}

void test_random_walk_restart() {
    const std::vector<Position> active{
        Position{0, 0}, Position{0, 1}, Position{1, 0},
        Position{2, 0}, Position{2, 1}, Position{2, 2},
    };
    std::map<Position, double> weights;
    for (const auto& position : active) {
        weights[position] = 0.1;
    }
    const GridGraph graph = build_manual_graph(active, weights);

    bool observed_restart = false;
    for (unsigned int seed = 0; seed < 128U && !observed_restart; ++seed) {
        RandomWalkStepper walker(graph, seed);
        std::vector<std::string> history;
        for (int step = 0; step < 40; ++step) {
            history.push_back(walker.step().status);
            if (walker.is_finished()) {
                break;
            }
        }
        const bool has_dead_end = std::find(history.begin(), history.end(), "Callejón sin salida") != history.end();
        observed_restart = has_dead_end && walker.result().found && walker.result().path.back() == graph.goal;
    }
    expect(observed_restart, "random walk should demonstrate restart and eventual success for some deterministic seed");
}

void test_controller() {
    SimulationController controller;
    controller.generate_graph(GraphConfig(5, 0.6, 80, 9U));

    const auto snapshots = controller.snapshots();
    expect(snapshots.size() == 4, "controller should expose four snapshots");
    for (const auto& [_, snapshot] : snapshots) {
        expect(snapshot.result.ticks == 0, "controller initial ticks should be zero");
    }

    controller.start();
    const auto stepped = controller.step_all();
    for (const auto& [_, snapshot] : stepped) {
        expect(snapshot.result.ticks == 1, "controller stepped ticks should be one");
    }

    controller.pause();
    expect(!controller.running(), "controller pause should stop running");

    controller.reset();
    const auto reset_snapshots = controller.snapshots();
    for (const auto& [_, snapshot] : reset_snapshots) {
        expect(snapshot.result.ticks == 0, "controller reset ticks should be zero");
    }

    const auto parity = run_python_scenario("controller_ticks");
    expect_equal("bfs,dfs,dijkstra,random", parity.at("keys"), "controller keys parity");
    expect_equal("0,0,0,0", parity.at("initial_ticks"), "controller initial ticks parity");
    expect_equal("1,1,1,1", parity.at("stepped_ticks"), "controller stepped ticks parity");
    expect_equal("0,0,0,0", parity.at("reset_ticks"), "controller reset ticks parity");
    expect_equal("0", parity.at("running_after_pause"), "controller running parity");
}

}  // namespace

int main() {
    const std::vector<std::pair<std::string, std::function<void()>>> tests{
        {"GraphConfig", test_graph_config},
        {"FactoryClamp", test_factory_clamp},
        {"SingleVertex", test_single_vertex},
        {"ManualAlgorithms", test_manual_algorithms},
        {"RandomWalkRestart", test_random_walk_restart},
        {"Controller", test_controller},
    };

    int failures = 0;
    for (const auto& [name, test] : tests) {
        try {
            test();
            std::cout << "[PASS] " << name << '\n';
        } catch (const std::exception& error) {
            ++failures;
            std::cerr << "[FAIL] " << name << ": " << error.what() << '\n';
        }
    }

    return failures == 0 ? EXIT_SUCCESS : EXIT_FAILURE;
}
