from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from grafos_ui.algorithms import (
    BreadthFirstStepper,
    DepthFirstStepper,
    DijkstraStepper,
    RandomWalkStepper,
)
from grafos_ui.controller import SimulationController
from grafos_ui.domain import GraphConfig, GridGraph, Position, Vertex
from grafos_ui.generator import GridGraphFactory, minimum_density


def run_until_finished(stepper, max_steps: int = 200) -> None:
    for _ in range(max_steps):
        if stepper.is_finished:
            return
        stepper.step()
    raise AssertionError(f"{stepper.display_name} did not finish in {max_steps} steps")


def build_manual_graph(active: set[Position], weights: dict[Position, float], size: int = 3) -> GridGraph:
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


class GraphConfigTests(unittest.TestCase):
    def test_size_must_be_in_range(self) -> None:
        with self.assertRaises(ValueError):
            GraphConfig(size=0, density=0.5, tick_ms=100)
        with self.assertRaises(ValueError):
            GraphConfig(size=101, density=0.5, tick_ms=100)

    def test_density_must_be_normalized(self) -> None:
        with self.assertRaises(ValueError):
            GraphConfig(size=4, density=-0.1, tick_ms=100)
        with self.assertRaises(ValueError):
            GraphConfig(size=4, density=1.1, tick_ms=100)


class GraphFactoryTests(unittest.TestCase):
    def test_generator_clamps_density_and_preserves_connectivity(self) -> None:
        config = GraphConfig(size=4, density=0.10, tick_ms=100, seed=7)
        graph, metadata = GridGraphFactory().build(config)

        self.assertTrue(metadata.was_clamped)
        self.assertAlmostEqual(metadata.min_density, minimum_density(4))
        self.assertGreaterEqual(graph.actual_density, metadata.min_density)
        self.assertEqual(graph.start, (0, 0))
        self.assertEqual(graph.goal, (3, 3))

        for position in graph.active_positions:
            self.assertGreater(len(graph.neighbors(position)), 0)

        bfs = BreadthFirstStepper(graph)
        run_until_finished(bfs)
        self.assertTrue(bfs.result.found)
        self.assertEqual(bfs.result.path[0], graph.start)
        self.assertEqual(bfs.result.path[-1], graph.goal)

    def test_single_vertex_graph_is_trivial(self) -> None:
        graph, metadata = GridGraphFactory().build(
            GraphConfig(size=1, density=1.0, tick_ms=100, seed=1)
        )

        self.assertEqual(graph.start, graph.goal)
        self.assertEqual(graph.actual_density, 0.0)
        self.assertEqual(metadata.actual_density, 0.0)

        dijkstra = DijkstraStepper(graph)
        self.assertTrue(dijkstra.is_finished)
        self.assertEqual(dijkstra.result.path_nodes, 1)
        self.assertEqual(dijkstra.result.path_edges, 0)
        self.assertEqual(dijkstra.result.total_cost, 0.0)


class AlgorithmTests(unittest.TestCase):
    def setUp(self) -> None:
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
        self.graph = build_manual_graph(active, weights)

    def test_bfs_returns_shortest_path_by_edges(self) -> None:
        bfs = BreadthFirstStepper(self.graph)
        run_until_finished(bfs)

        self.assertTrue(bfs.result.found)
        self.assertEqual(
            bfs.result.path,
            ((0, 0), (0, 1), (0, 2), (1, 2), (2, 2)),
        )
        self.assertEqual(bfs.result.path_edges, 4)

    def test_dfs_returns_a_valid_path(self) -> None:
        dfs = DepthFirstStepper(self.graph)
        run_until_finished(dfs)

        self.assertTrue(dfs.result.found)
        self.assertEqual(dfs.result.path[0], self.graph.start)
        self.assertEqual(dfs.result.path[-1], self.graph.goal)
        for left, right in zip(dfs.result.path, dfs.result.path[1:]):
            self.assertIn(right, self.graph.neighbors(left))

    def test_dijkstra_uses_vertex_weights(self) -> None:
        dijkstra = DijkstraStepper(self.graph)
        run_until_finished(dijkstra)

        self.assertTrue(dijkstra.result.found)
        self.assertEqual(
            dijkstra.result.path,
            ((0, 0), (1, 0), (2, 0), (2, 1), (2, 2)),
        )
        self.assertAlmostEqual(dijkstra.result.total_cost or 0.0, 0.4, places=6)

    def test_random_walk_restarts_after_dead_end(self) -> None:
        active = {
            (0, 0),
            (0, 1),
            (1, 0),
            (2, 0),
            (2, 1),
            (2, 2),
        }
        weights = {position: 0.1 for position in active}
        graph = build_manual_graph(active, weights)

        walker = RandomWalkStepper(graph, seed=1)
        history: list[str] = []
        for _ in range(20):
            history.append(walker.step().status)
            if walker.is_finished:
                break

        self.assertIn("Callejón sin salida", history)
        self.assertTrue(walker.result.found)
        self.assertEqual(walker.result.path[-1], graph.goal)


class ControllerTests(unittest.TestCase):
    def test_controller_keeps_steppers_synchronized(self) -> None:
        controller = SimulationController()
        controller.generate_graph(GraphConfig(size=5, density=0.6, tick_ms=80, seed=9))

        snapshots = controller.snapshots()
        self.assertEqual(set(snapshots), {"bfs", "dfs", "dijkstra", "random"})
        self.assertTrue(all(snapshot.result.ticks == 0 for snapshot in snapshots.values()))

        controller.start()
        stepped = controller.step_all()
        self.assertTrue(all(snapshot.result.ticks == 1 for snapshot in stepped.values()))

        controller.pause()
        self.assertFalse(controller.running)

        controller.reset()
        reset_snapshots = controller.snapshots()
        self.assertTrue(all(snapshot.result.ticks == 0 for snapshot in reset_snapshots.values()))
