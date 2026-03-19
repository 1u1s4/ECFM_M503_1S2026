from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_PROJECT = REPO_ROOT / "grafos_UI"
if str(PYTHON_PROJECT) not in sys.path:
    sys.path.insert(0, str(PYTHON_PROJECT))

from grafos_ui.algorithms import (  # noqa: E402
    BreadthFirstStepper,
    DepthFirstStepper,
    DijkstraStepper,
    RandomWalkStepper,
)
from grafos_ui.controller import SimulationController  # noqa: E402
from grafos_ui.domain import GraphConfig, GridGraph, Position, Vertex  # noqa: E402
from grafos_ui.generator import GridGraphFactory, minimum_density  # noqa: E402


def format_path(path: tuple[Position, ...]) -> str:
    return ";".join(f"{row},{col}" for row, col in path)


def build_manual_graph(
    active: set[Position],
    weights: dict[Position, float],
    size: int = 3,
) -> GridGraph:
    vertices: dict[Position, Vertex] = {}
    for row in range(size):
        for col in range(size):
            position = (row, col)
            is_active = position in active
            vertices[position] = Vertex(
                row=row,
                col=col,
                weight=weights.get(position, 0.0) if is_active else 0.0,
                active=is_active,
            )
    return GridGraph(
        size=size,
        vertices=vertices,
        start=(0, 0),
        goal=(size - 1, size - 1),
        actual_density=len(active) / (size * size),
        active_vertices=len(active),
        total_vertices=size * size,
    )


def run_until_finished(stepper, max_steps: int = 200) -> None:
    for _ in range(max_steps):
        if stepper.is_finished:
            return
        stepper.step()
    raise RuntimeError(f"{stepper.display_name} did not finish")


def scenario_manual_algorithms() -> dict[str, str]:
    active = {
        (0, 0),
        (0, 1),
        (0, 2),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
        (2, 2),
    }
    weights = {
        (0, 0): 0.0,
        (0, 1): 0.9,
        (0, 2): 0.9,
        (1, 0): 0.1,
        (1, 2): 0.9,
        (2, 0): 0.1,
        (2, 1): 0.1,
        (2, 2): 0.1,
    }
    graph = build_manual_graph(active, weights)

    bfs = BreadthFirstStepper(graph)
    dfs = DepthFirstStepper(graph)
    dijkstra = DijkstraStepper(graph)
    run_until_finished(bfs)
    run_until_finished(dfs)
    run_until_finished(dijkstra)

    return {
        "bfs_path": format_path(bfs.result.path),
        "dfs_start": f"{dfs.result.path[0][0]},{dfs.result.path[0][1]}",
        "dfs_end": f"{dfs.result.path[-1][0]},{dfs.result.path[-1][1]}",
        "dijkstra_path": format_path(dijkstra.result.path),
        "dijkstra_cost": f"{(dijkstra.result.total_cost or 0.0):.6f}",
    }


def scenario_factory_clamp() -> dict[str, str]:
    config = GraphConfig(size=4, density=0.10, tick_ms=100, seed=7)
    graph, metadata = GridGraphFactory().build(config)
    bfs = BreadthFirstStepper(graph)
    run_until_finished(bfs)
    return {
        "was_clamped": "1" if metadata.was_clamped else "0",
        "min_density": f"{minimum_density(4):.6f}",
        "actual_density": f"{graph.actual_density:.6f}",
        "start": f"{graph.start[0]},{graph.start[1]}",
        "goal": f"{graph.goal[0]},{graph.goal[1]}",
        "bfs_found": "1" if bfs.result.found else "0",
    }


def scenario_single_vertex() -> dict[str, str]:
    graph, metadata = GridGraphFactory().build(
        GraphConfig(size=1, density=1.0, tick_ms=100, seed=1)
    )
    dijkstra = DijkstraStepper(graph)
    return {
        "start": f"{graph.start[0]},{graph.start[1]}",
        "goal": f"{graph.goal[0]},{graph.goal[1]}",
        "graph_density": f"{graph.actual_density:.6f}",
        "metadata_density": f"{metadata.actual_density:.6f}",
        "path_nodes": str(dijkstra.result.path_nodes),
        "path_edges": str(dijkstra.result.path_edges),
        "total_cost": f"{(dijkstra.result.total_cost or 0.0):.6f}",
    }


def scenario_controller_ticks() -> dict[str, str]:
    controller = SimulationController()
    controller.generate_graph(GraphConfig(size=5, density=0.6, tick_ms=80, seed=9))

    snapshots = controller.snapshots()
    controller.start()
    stepped = controller.step_all()
    controller.pause()
    controller.reset()
    reset_snapshots = controller.snapshots()

    return {
        "keys": ",".join(sorted(snapshots)),
        "initial_ticks": ",".join(str(snapshot.result.ticks) for snapshot in snapshots.values()),
        "stepped_ticks": ",".join(str(snapshot.result.ticks) for snapshot in stepped.values()),
        "reset_ticks": ",".join(str(snapshot.result.ticks) for snapshot in reset_snapshots.values()),
        "running_after_pause": "1" if controller.running else "0",
    }


SCENARIOS = {
    "manual_algorithms": scenario_manual_algorithms,
    "factory_clamp": scenario_factory_clamp,
    "single_vertex": scenario_single_vertex,
    "controller_ticks": scenario_controller_ticks,
}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
        print("usage: py_reference.py <scenario>", file=sys.stderr)
        return 2

    for key, value in SCENARIOS[sys.argv[1]]().items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
