#pragma once

#include <array>
#include <map>
#include <memory>
#include <optional>
#include <string>

#include "grafos_cpp/algorithms.hpp"
#include "grafos_cpp/generator.hpp"

namespace grafos {

class SimulationController {
public:
    SimulationController();

    const GridGraph& generate_graph(const GraphConfig& config);
    void start();
    void pause();
    void reset();

    std::map<std::string, SearchSnapshot> step_all();
    std::map<std::string, SearchSnapshot> snapshots() const;

    bool running() const;
    const GraphConfig* config() const;
    const GridGraph* graph() const;
    const GenerationMetadata* metadata() const;

private:
    GridGraphFactory graph_factory_;
    std::optional<GraphConfig> config_;
    std::optional<GridGraph> graph_;
    std::optional<GenerationMetadata> metadata_;
    bool running_{false};
    unsigned int seed_anchor_{};
    std::map<std::string, std::unique_ptr<SearchStepper>> steppers_;

    static unsigned int random_seed();
    void rebuild_steppers();
};

}  // namespace grafos
