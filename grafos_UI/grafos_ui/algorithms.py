from __future__ import annotations

import heapq
import random
from abc import ABC, abstractmethod
from collections import deque
from itertools import count

from .domain import GridGraph, Position, SearchResult, SearchSnapshot


class SearchStepper(ABC):
    algorithm_id = "search"
    display_name = "Search"

    def __init__(self, graph: GridGraph, seed: int | None = None) -> None:
        self.graph = graph
        self.seed = seed
        self._rng = random.Random(seed)
        self.reset()

    def reset(self) -> None:
        self._ticks = 0
        self._finished = False
        self._found = False
        self._status = "Listo"
        self._current: Position | None = None
        self._path: tuple[Position, ...] = ()
        self._total_cost: float | None = None
        self._visited: set[Position] = set()
        self._parents: dict[Position, Position | None] = {}
        self._initialize()
        if self.graph.start == self.graph.goal:
            self._current = self.graph.start
            self._finish(found=True, path=(self.graph.start,), total_cost=0.0)

    @property
    def is_finished(self) -> bool:
        return self._finished

    @property
    def result(self) -> SearchResult:
        return SearchResult(
            found=self._found,
            path=self._path,
            ticks=self._ticks,
            visited_count=len(self._visited),
            frontier_size=len(self._frontier_positions()),
            path_nodes=len(self._path),
            path_edges=max(0, len(self._path) - 1),
            total_cost=self._total_cost,
        )

    def snapshot(self) -> SearchSnapshot:
        return SearchSnapshot(
            name=self.display_name,
            status=self._status,
            current=self._current,
            visited=tuple(sorted(self._visited)),
            frontier=tuple(sorted(self._frontier_positions())),
            path=self._path,
            result=self.result,
            metadata=self._metadata(),
        )

    def step(self) -> SearchSnapshot:
        if self._finished:
            return self.snapshot()
        self._ticks += 1
        self._step_impl()
        return self.snapshot()

    def _reconstruct_path(self, goal: Position) -> tuple[Position, ...]:
        path: list[Position] = []
        current: Position | None = goal
        while current is not None:
            path.append(current)
            current = self._parents.get(current)
        return tuple(reversed(path))

    def _finish(
        self,
        *,
        found: bool,
        path: tuple[Position, ...] = (),
        total_cost: float | None = None,
        status: str | None = None,
    ) -> None:
        self._finished = True
        self._found = found
        self._path = path
        self._total_cost = total_cost
        if status is not None:
            self._status = status
        elif found:
            self._status = "Encontrado"
        else:
            self._status = "Sin camino"

    def _metadata(self) -> dict[str, str]:
        return {}

    @abstractmethod
    def _initialize(self) -> None:
        pass

    @abstractmethod
    def _step_impl(self) -> None:
        pass

    @abstractmethod
    def _frontier_positions(self) -> tuple[Position, ...]:
        pass


class BreadthFirstStepper(SearchStepper):
    algorithm_id = "bfs"
    display_name = "BFS"

    def _initialize(self) -> None:
        self._queue: deque[Position] = deque([self.graph.start])
        self._parents = {self.graph.start: None}
        self._visited = {self.graph.start}

    def _step_impl(self) -> None:
        if not self._queue:
            self._finish(found=False)
            return

        node = self._queue.popleft()
        self._current = node
        self._status = "Explorando"
        if node == self.graph.goal:
            self._finish(found=True, path=self._reconstruct_path(node))
            return

        for neighbor in self.graph.neighbors(node):
            if neighbor in self._visited:
                continue
            self._visited.add(neighbor)
            self._parents[neighbor] = node
            self._queue.append(neighbor)

    def _frontier_positions(self) -> tuple[Position, ...]:
        return tuple(self._queue)


class DepthFirstStepper(SearchStepper):
    algorithm_id = "dfs"
    display_name = "DFS"

    def _initialize(self) -> None:
        self._stack: list[Position] = [self.graph.start]
        self._parents = {self.graph.start: None}
        self._visited = {self.graph.start}

    def _step_impl(self) -> None:
        if not self._stack:
            self._finish(found=False)
            return

        node = self._stack.pop()
        self._current = node
        self._status = "Explorando"
        if node == self.graph.goal:
            self._finish(found=True, path=self._reconstruct_path(node))
            return

        neighbors = self.graph.neighbors(node)
        for neighbor in reversed(neighbors):
            if neighbor in self._visited:
                continue
            self._visited.add(neighbor)
            self._parents[neighbor] = node
            self._stack.append(neighbor)

    def _frontier_positions(self) -> tuple[Position, ...]:
        return tuple(self._stack)


class DijkstraStepper(SearchStepper):
    algorithm_id = "dijkstra"
    display_name = "Dijkstra"

    def _initialize(self) -> None:
        self._counter = count()
        self._distances: dict[Position, float] = {self.graph.start: 0.0}
        self._settled: set[Position] = set()
        self._frontier: set[Position] = {self.graph.start}
        self._heap: list[tuple[float, int, Position]] = [
            (0.0, next(self._counter), self.graph.start)
        ]
        self._parents = {self.graph.start: None}
        self._visited = set()

    def _step_impl(self) -> None:
        while self._heap:
            current_cost, _, node = heapq.heappop(self._heap)
            if node in self._settled:
                continue
            break
        else:
            self._finish(found=False)
            return

        self._settled.add(node)
        self._frontier.discard(node)
        self._visited = set(self._settled)
        self._current = node
        self._status = "Explorando"

        if node == self.graph.goal:
            self._finish(
                found=True,
                path=self._reconstruct_path(node),
                total_cost=current_cost,
            )
            return

        for neighbor in self.graph.neighbors(node):
            if neighbor in self._settled:
                continue
            next_cost = current_cost + self.graph.vertex_at(neighbor).weight
            if next_cost < self._distances.get(neighbor, float("inf")):
                self._distances[neighbor] = next_cost
                self._parents[neighbor] = node
                heapq.heappush(self._heap, (next_cost, next(self._counter), neighbor))
                self._frontier.add(neighbor)

    def _frontier_positions(self) -> tuple[Position, ...]:
        return tuple(sorted(self._frontier))

    def _metadata(self) -> dict[str, str]:
        best_goal = self._distances.get(self.graph.goal)
        return {
            "Costo actual": "-" if best_goal is None else f"{best_goal:.3f}",
        }


class RandomWalkStepper(SearchStepper):
    algorithm_id = "random"
    display_name = "Random Walk"

    def _initialize(self) -> None:
        self._failed_attempts = 0
        self._pending_restart = False
        self._current = self.graph.start
        self._attempt_path: list[Position] = [self.graph.start]
        self._attempt_visited: set[Position] = {self.graph.start}
        self._global_visited: set[Position] = {self.graph.start}
        self._visited = set(self._global_visited)

    def _step_impl(self) -> None:
        if self._pending_restart:
            self._current = self.graph.start
            self._attempt_path = [self.graph.start]
            self._attempt_visited = {self.graph.start}
            self._pending_restart = False
            self._status = "Reintentando"
            return

        if self._current is None:
            self._current = self.graph.start

        if self._current == self.graph.goal:
            self._finish(found=True, path=tuple(self._attempt_path))
            return

        options = [
            neighbor
            for neighbor in self.graph.neighbors(self._current)
            if neighbor not in self._attempt_visited
        ]
        if not options:
            self._failed_attempts += 1
            self._pending_restart = True
            self._status = "Callejón sin salida"
            self._current = None
            return

        next_position = self._rng.choice(sorted(options))
        self._current = next_position
        self._attempt_path.append(next_position)
        self._attempt_visited.add(next_position)
        self._global_visited.add(next_position)
        self._visited = set(self._global_visited)
        self._status = "Explorando"

        if next_position == self.graph.goal:
            self._finish(found=True, path=tuple(self._attempt_path))

    def _frontier_positions(self) -> tuple[Position, ...]:
        if self._pending_restart or self._current is None:
            return ()
        options = [
            neighbor
            for neighbor in self.graph.neighbors(self._current)
            if neighbor not in self._attempt_visited
        ]
        return tuple(sorted(options))

    def snapshot(self) -> SearchSnapshot:
        base_snapshot = super().snapshot()
        return SearchSnapshot(
            name=base_snapshot.name,
            status=base_snapshot.status,
            current=base_snapshot.current,
            visited=base_snapshot.visited,
            frontier=base_snapshot.frontier,
            path=tuple(self._attempt_path if not self._found else self._path),
            result=base_snapshot.result,
            metadata=self._metadata(),
        )

    def _metadata(self) -> dict[str, str]:
        return {
            "Intentos fallidos": str(self._failed_attempts),
        }
