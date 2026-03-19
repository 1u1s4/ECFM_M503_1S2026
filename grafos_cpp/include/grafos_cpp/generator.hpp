#pragma once

#include <random>
#include <set>

#include "grafos_cpp/domain.hpp"

namespace grafos {

int minimum_active_vertices(int size);
double minimum_density(int size);

struct GraphBuildResult {
    GridGraph graph;
    GenerationMetadata metadata;
};

class GridGraphFactory {
public:
    GraphBuildResult build(const GraphConfig& config) const;

private:
    static std::set<Position> generate_connected_positions(
        int size,
        int target_active_vertices,
        std::mt19937& rng
    );
    static std::set<Position> build_seed_path(int size, std::mt19937& rng);
    static std::set<Position> frontier_candidates(
        int size,
        const std::set<Position>& active_positions
    );
    static std::map<Position, Vertex> build_vertices(
        int size,
        const std::set<Position>& active_positions,
        std::mt19937& rng
    );
    static unsigned int random_seed();
};

}  // namespace grafos
