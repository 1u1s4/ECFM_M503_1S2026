#include "grafos_cpp/controller.hpp"

#include <random>

namespace grafos {

SimulationController::SimulationController() : seed_anchor_(random_seed()) {}

const GridGraph& SimulationController::generate_graph(const GraphConfig& config) {
    pause();
    config_ = config;
    auto build = graph_factory_.build(config);
    graph_ = std::move(build.graph);
    metadata_ = std::move(build.metadata);
    seed_anchor_ = config.seed.value_or(seed_anchor_ + 97U);
    rebuild_steppers();
    return *graph_;
}

void SimulationController::start() {
    if (graph_.has_value()) {
        running_ = true;
    }
}

void SimulationController::pause() {
    running_ = false;
}

void SimulationController::reset() {
    pause();
    for (auto& [_, stepper] : steppers_) {
        stepper->reset();
    }
}

std::map<std::string, SearchSnapshot> SimulationController::step_all() {
    std::map<std::string, SearchSnapshot> snapshots;
    for (auto& [name, stepper] : steppers_) {
        snapshots[name] = stepper->step();
    }

    if (!snapshots.empty()) {
        bool all_finished = true;
        for (const auto& [_, stepper] : steppers_) {
            if (!stepper->is_finished()) {
                all_finished = false;
                break;
            }
        }
        if (all_finished) {
            running_ = false;
        }
    }
    return snapshots;
}

std::map<std::string, SearchSnapshot> SimulationController::snapshots() const {
    std::map<std::string, SearchSnapshot> snapshots;
    for (const auto& [name, stepper] : steppers_) {
        snapshots[name] = stepper->snapshot();
    }
    return snapshots;
}

bool SimulationController::running() const {
    return running_;
}

const GraphConfig* SimulationController::config() const {
    return config_.has_value() ? &*config_ : nullptr;
}

const GridGraph* SimulationController::graph() const {
    return graph_.has_value() ? &*graph_ : nullptr;
}

const GenerationMetadata* SimulationController::metadata() const {
    return metadata_.has_value() ? &*metadata_ : nullptr;
}

unsigned int SimulationController::random_seed() {
    std::random_device device;
    return device();
}

void SimulationController::rebuild_steppers() {
    steppers_.clear();
    if (!graph_.has_value()) {
        return;
    }

    steppers_["bfs"] = std::make_unique<BreadthFirstStepper>(*graph_, seed_anchor_ + 0U);
    steppers_["dfs"] = std::make_unique<DepthFirstStepper>(*graph_, seed_anchor_ + 1U);
    steppers_["dijkstra"] = std::make_unique<DijkstraStepper>(*graph_, seed_anchor_ + 2U);
    steppers_["random"] = std::make_unique<RandomWalkStepper>(*graph_, seed_anchor_ + 3U);
}

}  // namespace grafos
