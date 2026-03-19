#pragma once

#include <compare>
#include <map>
#include <optional>
#include <string>
#include <vector>

namespace grafos {

struct Position {
    int row{};
    int col{};

    auto operator<=>(const Position&) const = default;
};

struct PositionHash {
    std::size_t operator()(const Position& position) const noexcept;
};

std::string position_to_string(const Position& position);

struct GraphConfig {
    int size{};
    double density{};
    int tick_ms{};
    std::optional<unsigned int> seed{};

    GraphConfig(
        int size_,
        double density_,
        int tick_ms_,
        std::optional<unsigned int> seed_ = std::nullopt
    );

    int total_vertices() const;
};

struct Vertex {
    int row{};
    int col{};
    double weight{};
    bool active{};

    Position position() const;
};

struct GridGraph {
    int size{};
    std::map<Position, Vertex> vertices;
    Position start{};
    Position goal{};
    double actual_density{};
    int active_vertices{};
    int total_vertices{};

    const Vertex& vertex_at(const Position& position) const;
    bool is_active(const Position& position) const;
    std::vector<Position> neighbors(const Position& position) const;
    double path_cost(const std::vector<Position>& path) const;
    std::vector<Position> active_positions() const;
};

struct SearchResult {
    bool found{};
    std::vector<Position> path;
    int ticks{};
    int visited_count{};
    int frontier_size{};
    int path_nodes{};
    int path_edges{};
    std::optional<double> total_cost{};

    static SearchResult empty();
};

struct SearchSnapshot {
    std::string name;
    std::string status;
    std::optional<Position> current;
    std::vector<Position> visited;
    std::vector<Position> frontier;
    std::vector<Position> path;
    SearchResult result;
    std::map<std::string, std::string> metadata;
};

struct GenerationMetadata {
    double requested_density{};
    double applied_density{};
    double actual_density{};
    double min_density{};
    int active_vertices{};
    int total_vertices{};
    bool was_clamped{};

    std::string display_text() const;
};

struct DeviceInfo {
    std::string label;
    std::string detail;
    bool uses_gpu{};
};

}  // namespace grafos
