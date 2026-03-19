#pragma once

#include <deque>
#include <map>
#include <memory>
#include <optional>
#include <queue>
#include <random>
#include <set>
#include <string>
#include <vector>

#include "grafos_cpp/domain.hpp"

namespace grafos {

class SearchStepper {
public:
    SearchStepper(const GridGraph& graph, std::optional<unsigned int> seed = std::nullopt);
    virtual ~SearchStepper() = default;

    void reset();
    bool is_finished() const;
    SearchResult result() const;
    virtual SearchSnapshot snapshot() const;
    SearchSnapshot step();

    virtual std::string algorithm_id() const = 0;
    virtual std::string display_name() const = 0;

protected:
    const GridGraph& graph_;
    std::optional<unsigned int> seed_;
    std::mt19937 rng_;
    int ticks_{};
    bool finished_{};
    bool found_{};
    std::string status_{"Listo"};
    std::optional<Position> current_;
    std::vector<Position> path_;
    std::optional<double> total_cost_;
    std::set<Position> visited_;
    std::map<Position, std::optional<Position>> parents_;

    std::vector<Position> reconstruct_path(const Position& goal) const;
    void finish(
        bool found,
        std::vector<Position> path = {},
        std::optional<double> total_cost = std::nullopt,
        std::optional<std::string> status = std::nullopt
    );

    virtual std::map<std::string, std::string> metadata() const;
    virtual void initialize() = 0;
    virtual void step_impl() = 0;
    virtual std::vector<Position> frontier_positions() const = 0;
};

class BreadthFirstStepper : public SearchStepper {
public:
    explicit BreadthFirstStepper(const GridGraph& graph, std::optional<unsigned int> seed = std::nullopt);

    std::string algorithm_id() const override;
    std::string display_name() const override;

protected:
    void initialize() override;
    void step_impl() override;
    std::vector<Position> frontier_positions() const override;

private:
    std::deque<Position> queue_;
};

class DepthFirstStepper : public SearchStepper {
public:
    explicit DepthFirstStepper(const GridGraph& graph, std::optional<unsigned int> seed = std::nullopt);

    std::string algorithm_id() const override;
    std::string display_name() const override;

protected:
    void initialize() override;
    void step_impl() override;
    std::vector<Position> frontier_positions() const override;

private:
    std::vector<Position> stack_;
};

class DijkstraStepper : public SearchStepper {
public:
    explicit DijkstraStepper(const GridGraph& graph, std::optional<unsigned int> seed = std::nullopt);

    std::string algorithm_id() const override;
    std::string display_name() const override;

protected:
    void initialize() override;
    void step_impl() override;
    std::vector<Position> frontier_positions() const override;
    std::map<std::string, std::string> metadata() const override;

private:
    struct HeapNode {
        double cost{};
        long long order{};
        Position position{};
    };

    struct HeapCompare {
        bool operator()(const HeapNode& left, const HeapNode& right) const;
    };

    long long counter_{};
    std::map<Position, double> distances_;
    std::set<Position> settled_;
    std::set<Position> frontier_;
    std::priority_queue<HeapNode, std::vector<HeapNode>, HeapCompare> heap_;
};

class RandomWalkStepper : public SearchStepper {
public:
    explicit RandomWalkStepper(const GridGraph& graph, std::optional<unsigned int> seed = std::nullopt);

    std::string algorithm_id() const override;
    std::string display_name() const override;

    SearchSnapshot snapshot() const override;

protected:
    void initialize() override;
    void step_impl() override;
    std::vector<Position> frontier_positions() const override;
    std::map<std::string, std::string> metadata() const override;

private:
    int failed_attempts_{};
    bool pending_restart_{};
    std::vector<Position> attempt_path_;
    std::set<Position> attempt_visited_;
    std::set<Position> global_visited_;
};

}  // namespace grafos
