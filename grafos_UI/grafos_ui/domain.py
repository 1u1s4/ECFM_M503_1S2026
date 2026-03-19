from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

Position = tuple[int, int]


@dataclass(frozen=True, slots=True)
class GraphConfig:
    size: int
    density: float
    tick_ms: int
    seed: int | None = None

    def __post_init__(self) -> None:
        if not 1 <= self.size <= 100:
            raise ValueError("size must be in [1, 100]")
        if not 0.0 <= self.density <= 1.0:
            raise ValueError("density must be in [0, 1]")
        if self.tick_ms <= 0:
            raise ValueError("tick_ms must be positive")

    @property
    def total_vertices(self) -> int:
        return self.size * self.size


@dataclass(frozen=True, slots=True)
class Vertex:
    row: int
    col: int
    weight: float
    active: bool

    @property
    def position(self) -> Position:
        return (self.row, self.col)


@dataclass(frozen=True, slots=True)
class GridGraph:
    size: int
    vertices: Mapping[Position, Vertex]
    start: Position
    goal: Position
    actual_density: float
    active_vertices: int
    total_vertices: int

    def vertex_at(self, position: Position) -> Vertex:
        return self.vertices[position]

    def is_active(self, position: Position) -> bool:
        return self.vertices[position].active

    def neighbors(self, position: Position) -> tuple[Position, ...]:
        row, col = position
        candidates = (
            (row - 1, col),
            (row, col + 1),
            (row + 1, col),
            (row, col - 1),
        )
        valid: list[Position] = []
        for next_row, next_col in candidates:
            if 0 <= next_row < self.size and 0 <= next_col < self.size:
                candidate = (next_row, next_col)
                if self.is_active(candidate):
                    valid.append(candidate)
        return tuple(sorted(valid))

    def path_cost(self, path: tuple[Position, ...]) -> float:
        if not path:
            return 0.0
        return sum(self.vertex_at(position).weight for position in path[1:])

    @property
    def active_positions(self) -> tuple[Position, ...]:
        return tuple(
            sorted(position for position, vertex in self.vertices.items() if vertex.active)
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    found: bool
    path: tuple[Position, ...]
    ticks: int
    visited_count: int
    frontier_size: int
    path_nodes: int
    path_edges: int
    total_cost: float | None = None

    @classmethod
    def empty(cls) -> "SearchResult":
        return cls(
            found=False,
            path=(),
            ticks=0,
            visited_count=0,
            frontier_size=0,
            path_nodes=0,
            path_edges=0,
            total_cost=None,
        )


@dataclass(frozen=True, slots=True)
class SearchSnapshot:
    name: str
    status: str
    current: Position | None
    visited: tuple[Position, ...]
    frontier: tuple[Position, ...]
    path: tuple[Position, ...]
    result: SearchResult
    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GenerationMetadata:
    requested_density: float
    applied_density: float
    actual_density: float
    min_density: float
    active_vertices: int
    total_vertices: int
    was_clamped: bool

    @property
    def display_text(self) -> str:
        return (
            f"D solicitada {self.requested_density:.3f} | "
            f"D aplicada {self.applied_density:.3f} | "
            f"D real {self.actual_density:.3f} | "
            f"V_A {self.active_vertices}/{self.total_vertices}"
        )
