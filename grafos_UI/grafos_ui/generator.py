from __future__ import annotations

import random

from .domain import GenerationMetadata, GraphConfig, GridGraph, Position, Vertex


def minimum_active_vertices(size: int) -> int:
    if size <= 1:
        return 0
    return (2 * size) - 1


def minimum_density(size: int) -> float:
    if size <= 1:
        return 0.0
    total_vertices = size * size
    return minimum_active_vertices(size) / total_vertices


class GridGraphFactory:
    def __init__(self) -> None:
        self._system_rng = random.SystemRandom()

    def build(self, config: GraphConfig) -> tuple[GridGraph, GenerationMetadata]:
        rng = random.Random(config.seed if config.seed is not None else self._system_rng.randint(0, 10**9))

        if config.size == 1:
            vertex = Vertex(row=0, col=0, weight=0.0, active=True)
            graph = GridGraph(
                size=1,
                vertices={(0, 0): vertex},
                start=(0, 0),
                goal=(0, 0),
                actual_density=0.0,
                active_vertices=0,
                total_vertices=1,
            )
            metadata = GenerationMetadata(
                requested_density=config.density,
                applied_density=0.0,
                actual_density=0.0,
                min_density=0.0,
                active_vertices=0,
                total_vertices=1,
                was_clamped=False,
            )
            return graph, metadata

        min_density = minimum_density(config.size)
        applied_density = max(config.density, min_density)
        total_vertices = config.total_vertices
        target_active_vertices = max(
            minimum_active_vertices(config.size),
            min(total_vertices, round(applied_density * total_vertices)),
        )

        active_positions = self._generate_connected_positions(config.size, target_active_vertices, rng)
        vertices = self._build_vertices(config.size, active_positions, rng)
        actual_density = len(active_positions) / total_vertices

        graph = GridGraph(
            size=config.size,
            vertices=vertices,
            start=(0, 0),
            goal=(config.size - 1, config.size - 1),
            actual_density=actual_density,
            active_vertices=len(active_positions),
            total_vertices=total_vertices,
        )
        metadata = GenerationMetadata(
            requested_density=config.density,
            applied_density=applied_density,
            actual_density=actual_density,
            min_density=min_density,
            active_vertices=len(active_positions),
            total_vertices=total_vertices,
            was_clamped=config.density < min_density,
        )
        return graph, metadata

    def _generate_connected_positions(
        self,
        size: int,
        target_active_vertices: int,
        rng: random.Random,
    ) -> set[Position]:
        active_positions = self._build_seed_path(size, rng)

        while len(active_positions) < target_active_vertices:
            frontier = sorted(self._frontier_candidates(size, active_positions))
            if not frontier:
                break
            active_positions.add(rng.choice(frontier))

        return active_positions

    def _build_seed_path(self, size: int, rng: random.Random) -> set[Position]:
        path_steps = ["R"] * (size - 1) + ["D"] * (size - 1)
        rng.shuffle(path_steps)

        row, col = 0, 0
        active_positions: set[Position] = {(row, col)}
        for step in path_steps:
            if step == "R":
                col += 1
            else:
                row += 1
            active_positions.add((row, col))
        return active_positions

    def _frontier_candidates(self, size: int, active_positions: set[Position]) -> set[Position]:
        frontier: set[Position] = set()
        for row, col in active_positions:
            for next_row, next_col in (
                (row - 1, col),
                (row, col + 1),
                (row + 1, col),
                (row, col - 1),
            ):
                if 0 <= next_row < size and 0 <= next_col < size:
                    candidate = (next_row, next_col)
                    if candidate not in active_positions:
                        frontier.add(candidate)
        return frontier

    def _build_vertices(
        self,
        size: int,
        active_positions: set[Position],
        rng: random.Random,
    ) -> dict[Position, Vertex]:
        vertices: dict[Position, Vertex] = {}
        for row in range(size):
            for col in range(size):
                position = (row, col)
                is_active = position in active_positions
                vertices[position] = Vertex(
                    row=row,
                    col=col,
                    weight=rng.random() if is_active else 0.0,
                    active=is_active,
                )
        return vertices
