#include "grafos_cpp/algorithms.hpp"

#include <algorithm>
#include <limits>
#include <sstream>

namespace grafos {

SearchStepper::SearchStepper(const GridGraph& graph, const std::optional<unsigned int> seed)
    : graph_(graph), seed_(seed), rng_(seed.value_or(std::random_device{}())) {}

void SearchStepper::reset() {
    ticks_ = 0;
    finished_ = false;
    found_ = false;
    status_ = "Listo";
    current_ = std::nullopt;
    path_.clear();
    total_cost_ = std::nullopt;
    visited_.clear();
    parents_.clear();
    initialize();
    if (graph_.start == graph_.goal) {
        current_ = graph_.start;
        finish(true, {graph_.start}, 0.0);
    }
}

bool SearchStepper::is_finished() const {
    return finished_;
}

SearchResult SearchStepper::result() const {
    return SearchResult{
        found_,
        path_,
        ticks_,
        static_cast<int>(visited_.size()),
        static_cast<int>(frontier_positions().size()),
        static_cast<int>(path_.size()),
        std::max(0, static_cast<int>(path_.size()) - 1),
        total_cost_,
    };
}

SearchSnapshot SearchStepper::snapshot() const {
    return SearchSnapshot{
        display_name(),
        status_,
        current_,
        std::vector<Position>(visited_.begin(), visited_.end()),
        frontier_positions(),
        path_,
        result(),
        metadata(),
    };
}

SearchSnapshot SearchStepper::step() {
    if (finished_) {
        return snapshot();
    }
    ++ticks_;
    step_impl();
    return snapshot();
}

std::vector<Position> SearchStepper::reconstruct_path(const Position& goal) const {
    std::vector<Position> path;
    std::optional<Position> current = goal;
    while (current.has_value()) {
        path.push_back(*current);
        const auto it = parents_.find(*current);
        current = it == parents_.end() ? std::nullopt : it->second;
    }
    std::reverse(path.begin(), path.end());
    return path;
}

void SearchStepper::finish(
    const bool found,
    std::vector<Position> path,
    const std::optional<double> total_cost,
    const std::optional<std::string> status
) {
    finished_ = true;
    found_ = found;
    path_ = std::move(path);
    total_cost_ = total_cost;
    if (status.has_value()) {
        status_ = *status;
    } else if (found) {
        status_ = "Encontrado";
    } else {
        status_ = "Sin camino";
    }
}

std::map<std::string, std::string> SearchStepper::metadata() const {
    return {};
}

BreadthFirstStepper::BreadthFirstStepper(const GridGraph& graph, const std::optional<unsigned int> seed)
    : SearchStepper(graph, seed) {
    reset();
}

std::string BreadthFirstStepper::algorithm_id() const {
    return "bfs";
}

std::string BreadthFirstStepper::display_name() const {
    return "BFS";
}

void BreadthFirstStepper::initialize() {
    queue_.clear();
    queue_.push_back(graph_.start);
    parents_[graph_.start] = std::nullopt;
    visited_.insert(graph_.start);
}

void BreadthFirstStepper::step_impl() {
    if (queue_.empty()) {
        finish(false);
        return;
    }

    const Position node = queue_.front();
    queue_.pop_front();
    current_ = node;
    status_ = "Explorando";
    if (node == graph_.goal) {
        finish(true, reconstruct_path(node));
        return;
    }

    for (const auto& neighbor : graph_.neighbors(node)) {
        if (visited_.contains(neighbor)) {
            continue;
        }
        visited_.insert(neighbor);
        parents_[neighbor] = node;
        queue_.push_back(neighbor);
    }
}

std::vector<Position> BreadthFirstStepper::frontier_positions() const {
    return std::vector<Position>(queue_.begin(), queue_.end());
}

DepthFirstStepper::DepthFirstStepper(const GridGraph& graph, const std::optional<unsigned int> seed)
    : SearchStepper(graph, seed) {
    reset();
}

std::string DepthFirstStepper::algorithm_id() const {
    return "dfs";
}

std::string DepthFirstStepper::display_name() const {
    return "DFS";
}

void DepthFirstStepper::initialize() {
    stack_.clear();
    stack_.push_back(graph_.start);
    parents_[graph_.start] = std::nullopt;
    visited_.insert(graph_.start);
}

void DepthFirstStepper::step_impl() {
    if (stack_.empty()) {
        finish(false);
        return;
    }

    const Position node = stack_.back();
    stack_.pop_back();
    current_ = node;
    status_ = "Explorando";
    if (node == graph_.goal) {
        finish(true, reconstruct_path(node));
        return;
    }

    auto neighbors = graph_.neighbors(node);
    std::reverse(neighbors.begin(), neighbors.end());
    for (const auto& neighbor : neighbors) {
        if (visited_.contains(neighbor)) {
            continue;
        }
        visited_.insert(neighbor);
        parents_[neighbor] = node;
        stack_.push_back(neighbor);
    }
}

std::vector<Position> DepthFirstStepper::frontier_positions() const {
    return stack_;
}

DijkstraStepper::DijkstraStepper(const GridGraph& graph, const std::optional<unsigned int> seed)
    : SearchStepper(graph, seed) {
    reset();
}

bool DijkstraStepper::HeapCompare::operator()(const HeapNode& left, const HeapNode& right) const {
    if (left.cost != right.cost) {
        return left.cost > right.cost;
    }
    return left.order > right.order;
}

std::string DijkstraStepper::algorithm_id() const {
    return "dijkstra";
}

std::string DijkstraStepper::display_name() const {
    return "Dijkstra";
}

void DijkstraStepper::initialize() {
    counter_ = 0;
    distances_.clear();
    settled_.clear();
    frontier_.clear();
    heap_ = {};
    distances_[graph_.start] = 0.0;
    frontier_.insert(graph_.start);
    heap_.push(HeapNode{0.0, counter_++, graph_.start});
    parents_[graph_.start] = std::nullopt;
    visited_.clear();
}

void DijkstraStepper::step_impl() {
    HeapNode next_node;
    bool found_node = false;
    while (!heap_.empty()) {
        next_node = heap_.top();
        heap_.pop();
        if (settled_.contains(next_node.position)) {
            continue;
        }
        found_node = true;
        break;
    }

    if (!found_node) {
        finish(false);
        return;
    }

    settled_.insert(next_node.position);
    frontier_.erase(next_node.position);
    visited_ = settled_;
    current_ = next_node.position;
    status_ = "Explorando";

    if (next_node.position == graph_.goal) {
        finish(true, reconstruct_path(next_node.position), next_node.cost);
        return;
    }

    for (const auto& neighbor : graph_.neighbors(next_node.position)) {
        if (settled_.contains(neighbor)) {
            continue;
        }
        const double next_cost = next_node.cost + graph_.vertex_at(neighbor).weight;
        const auto current_best = distances_.contains(neighbor)
                                ? distances_[neighbor]
                                : std::numeric_limits<double>::infinity();
        if (next_cost < current_best) {
            distances_[neighbor] = next_cost;
            parents_[neighbor] = next_node.position;
            heap_.push(HeapNode{next_cost, counter_++, neighbor});
            frontier_.insert(neighbor);
        }
    }
}

std::vector<Position> DijkstraStepper::frontier_positions() const {
    return std::vector<Position>(frontier_.begin(), frontier_.end());
}

std::map<std::string, std::string> DijkstraStepper::metadata() const {
    std::map<std::string, std::string> data;
    const auto it = distances_.find(graph_.goal);
    if (it == distances_.end()) {
        data["Costo actual"] = "-";
        return data;
    }
    std::ostringstream buffer;
    buffer.setf(std::ios::fixed);
    buffer.precision(3);
    buffer << it->second;
    data["Costo actual"] = buffer.str();
    return data;
}

RandomWalkStepper::RandomWalkStepper(const GridGraph& graph, const std::optional<unsigned int> seed)
    : SearchStepper(graph, seed) {
    reset();
}

std::string RandomWalkStepper::algorithm_id() const {
    return "random";
}

std::string RandomWalkStepper::display_name() const {
    return "Random Walk";
}

SearchSnapshot RandomWalkStepper::snapshot() const {
    auto base = SearchStepper::snapshot();
    base.path = found_ ? path_ : attempt_path_;
    base.metadata = metadata();
    return base;
}

void RandomWalkStepper::initialize() {
    failed_attempts_ = 0;
    pending_restart_ = false;
    current_ = graph_.start;
    attempt_path_ = {graph_.start};
    attempt_visited_ = {graph_.start};
    global_visited_ = {graph_.start};
    visited_ = global_visited_;
}

void RandomWalkStepper::step_impl() {
    if (pending_restart_) {
        current_ = graph_.start;
        attempt_path_ = {graph_.start};
        attempt_visited_ = {graph_.start};
        pending_restart_ = false;
        status_ = "Reintentando";
        return;
    }

    if (!current_.has_value()) {
        current_ = graph_.start;
    }

    if (*current_ == graph_.goal) {
        finish(true, attempt_path_);
        return;
    }

    std::vector<Position> options;
    for (const auto& neighbor : graph_.neighbors(*current_)) {
        if (!attempt_visited_.contains(neighbor)) {
            options.push_back(neighbor);
        }
    }

    if (options.empty()) {
        ++failed_attempts_;
        pending_restart_ = true;
        status_ = "Callejón sin salida";
        current_ = std::nullopt;
        return;
    }

    std::uniform_int_distribution<std::size_t> distribution(0, options.size() - 1);
    const Position next_position = options[distribution(rng_)];
    current_ = next_position;
    attempt_path_.push_back(next_position);
    attempt_visited_.insert(next_position);
    global_visited_.insert(next_position);
    visited_ = global_visited_;
    status_ = "Explorando";

    if (next_position == graph_.goal) {
        finish(true, attempt_path_);
    }
}

std::vector<Position> RandomWalkStepper::frontier_positions() const {
    if (pending_restart_ || !current_.has_value()) {
        return {};
    }

    std::vector<Position> options;
    for (const auto& neighbor : graph_.neighbors(*current_)) {
        if (!attempt_visited_.contains(neighbor)) {
            options.push_back(neighbor);
        }
    }
    std::sort(options.begin(), options.end());
    return options;
}

std::map<std::string, std::string> RandomWalkStepper::metadata() const {
    return {{"Intentos fallidos", std::to_string(failed_attempts_)}};
}

}  // namespace grafos
