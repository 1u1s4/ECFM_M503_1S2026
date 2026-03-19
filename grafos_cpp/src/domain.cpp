#include "grafos_cpp/domain.hpp"

#include <array>
#include <algorithm>
#include <iomanip>
#include <sstream>
#include <stdexcept>

namespace grafos {

std::size_t PositionHash::operator()(const Position& position) const noexcept {
    return (static_cast<std::size_t>(position.row) << 32U)
         ^ static_cast<std::size_t>(position.col);
}

std::string position_to_string(const Position& position) {
    return "(" + std::to_string(position.row) + "," + std::to_string(position.col) + ")";
}

GraphConfig::GraphConfig(
    int size_,
    double density_,
    int tick_ms_,
    std::optional<unsigned int> seed_
) : size(size_), density(density_), tick_ms(tick_ms_), seed(seed_) {
    if (size < 1 || size > 100) {
        throw std::invalid_argument("size must be in [1, 100]");
    }
    if (density < 0.0 || density > 1.0) {
        throw std::invalid_argument("density must be in [0, 1]");
    }
    if (tick_ms <= 0) {
        throw std::invalid_argument("tick_ms must be positive");
    }
}

int GraphConfig::total_vertices() const {
    return size * size;
}

Position Vertex::position() const {
    return Position{row, col};
}

const Vertex& GridGraph::vertex_at(const Position& position) const {
    return vertices.at(position);
}

bool GridGraph::is_active(const Position& position) const {
    return vertex_at(position).active;
}

std::vector<Position> GridGraph::neighbors(const Position& position) const {
    const std::array<Position, 4> candidates{
        Position{position.row - 1, position.col},
        Position{position.row, position.col + 1},
        Position{position.row + 1, position.col},
        Position{position.row, position.col - 1},
    };

    std::vector<Position> valid;
    for (const auto& candidate : candidates) {
        if (candidate.row < 0 || candidate.row >= size || candidate.col < 0 || candidate.col >= size) {
            continue;
        }
        if (is_active(candidate)) {
            valid.push_back(candidate);
        }
    }
    std::sort(valid.begin(), valid.end());
    return valid;
}

double GridGraph::path_cost(const std::vector<Position>& path) const {
    if (path.empty()) {
        return 0.0;
    }
    double total = 0.0;
    for (std::size_t index = 1; index < path.size(); ++index) {
        total += vertex_at(path[index]).weight;
    }
    return total;
}

std::vector<Position> GridGraph::active_positions() const {
    std::vector<Position> positions;
    for (const auto& [position, vertex] : vertices) {
        if (vertex.active) {
            positions.push_back(position);
        }
    }
    std::sort(positions.begin(), positions.end());
    return positions;
}

SearchResult SearchResult::empty() {
    return SearchResult{
        false,
        {},
        0,
        0,
        0,
        0,
        0,
        std::nullopt,
    };
}

std::string GenerationMetadata::display_text() const {
    std::ostringstream buffer;
    buffer << std::fixed << std::setprecision(3)
           << "D solicitada " << requested_density
           << " | D aplicada " << applied_density
           << " | D real " << actual_density
           << " | V_A " << active_vertices << "/" << total_vertices;
    return buffer.str();
}

}  // namespace grafos
