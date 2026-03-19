#include "grafos_cpp/generator.hpp"

#include <algorithm>
#include <cmath>

namespace grafos {

namespace {

template <typename T>
const T& choose_one(const std::vector<T>& values, std::mt19937& rng) {
    std::uniform_int_distribution<std::size_t> distribution(0, values.size() - 1);
    return values[distribution(rng)];
}

}  // namespace

int minimum_active_vertices(const int size) {
    if (size <= 1) {
        return 0;
    }
    return (2 * size) - 1;
}

double minimum_density(const int size) {
    if (size <= 1) {
        return 0.0;
    }
    const auto total_vertices = size * size;
    return static_cast<double>(minimum_active_vertices(size)) / static_cast<double>(total_vertices);
}

GraphBuildResult GridGraphFactory::build(const GraphConfig& config) const {
    std::mt19937 rng(config.seed.value_or(random_seed()));

    if (config.size == 1) {
        Vertex vertex{0, 0, 0.0, true};
        GraphBuildResult result;
        result.graph = GridGraph{
            1,
            {{Position{0, 0}, vertex}},
            Position{0, 0},
            Position{0, 0},
            0.0,
            0,
            1,
        };
        result.metadata = GenerationMetadata{
            config.density,
            0.0,
            0.0,
            0.0,
            0,
            1,
            false,
        };
        return result;
    }

    const double min_density_value = minimum_density(config.size);
    const double applied_density = std::max(config.density, min_density_value);
    const int total_vertices = config.total_vertices();
    const int target_active_vertices = std::max(
        minimum_active_vertices(config.size),
        std::min(
            total_vertices,
            static_cast<int>(std::llround(applied_density * static_cast<double>(total_vertices)))
        )
    );

    const auto active_positions = generate_connected_positions(config.size, target_active_vertices, rng);
    const auto vertices = build_vertices(config.size, active_positions, rng);
    const double actual_density = static_cast<double>(active_positions.size())
                                / static_cast<double>(total_vertices);

    GraphBuildResult result;
    result.graph = GridGraph{
        config.size,
        vertices,
        Position{0, 0},
        Position{config.size - 1, config.size - 1},
        actual_density,
        static_cast<int>(active_positions.size()),
        total_vertices,
    };
    result.metadata = GenerationMetadata{
        config.density,
        applied_density,
        actual_density,
        min_density_value,
        static_cast<int>(active_positions.size()),
        total_vertices,
        config.density < min_density_value,
    };
    return result;
}

std::set<Position> GridGraphFactory::generate_connected_positions(
    const int size,
    const int target_active_vertices,
    std::mt19937& rng
) {
    auto active_positions = build_seed_path(size, rng);

    while (static_cast<int>(active_positions.size()) < target_active_vertices) {
        const auto frontier_set = frontier_candidates(size, active_positions);
        if (frontier_set.empty()) {
            break;
        }
        std::vector<Position> frontier(frontier_set.begin(), frontier_set.end());
        active_positions.insert(choose_one(frontier, rng));
    }

    return active_positions;
}

std::set<Position> GridGraphFactory::build_seed_path(const int size, std::mt19937& rng) {
    std::vector<char> path_steps;
    path_steps.insert(path_steps.end(), size - 1, 'R');
    path_steps.insert(path_steps.end(), size - 1, 'D');
    std::shuffle(path_steps.begin(), path_steps.end(), rng);

    int row = 0;
    int col = 0;
    std::set<Position> active_positions{{Position{row, col}}};
    for (const char step : path_steps) {
        if (step == 'R') {
            ++col;
        } else {
            ++row;
        }
        active_positions.insert(Position{row, col});
    }
    return active_positions;
}

std::set<Position> GridGraphFactory::frontier_candidates(
    const int size,
    const std::set<Position>& active_positions
) {
    std::set<Position> frontier;
    for (const auto& position : active_positions) {
        const std::array<Position, 4> candidates{
            Position{position.row - 1, position.col},
            Position{position.row, position.col + 1},
            Position{position.row + 1, position.col},
            Position{position.row, position.col - 1},
        };
        for (const auto& candidate : candidates) {
            if (candidate.row < 0 || candidate.row >= size || candidate.col < 0 || candidate.col >= size) {
                continue;
            }
            if (!active_positions.contains(candidate)) {
                frontier.insert(candidate);
            }
        }
    }
    return frontier;
}

std::map<Position, Vertex> GridGraphFactory::build_vertices(
    const int size,
    const std::set<Position>& active_positions,
    std::mt19937& rng
) {
    std::uniform_real_distribution<double> distribution(0.0, 1.0);

    std::map<Position, Vertex> vertices;
    for (int row = 0; row < size; ++row) {
        for (int col = 0; col < size; ++col) {
            const Position position{row, col};
            const bool is_active = active_positions.contains(position);
            vertices[position] = Vertex{
                row,
                col,
                is_active ? distribution(rng) : 0.0,
                is_active,
            };
        }
    }
    return vertices;
}

unsigned int GridGraphFactory::random_seed() {
    std::random_device device;
    return device();
}

}  // namespace grafos
