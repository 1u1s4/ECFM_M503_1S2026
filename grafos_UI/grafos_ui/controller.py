from __future__ import annotations

import random
from collections.abc import Sequence

from .algorithms import (
    BreadthFirstStepper,
    DepthFirstStepper,
    DijkstraStepper,
    RandomWalkStepper,
    SearchStepper,
)
from .domain import GenerationMetadata, GraphConfig, GridGraph, SearchSnapshot
from .generator import GridGraphFactory


class SimulationController:
    def __init__(
        self,
        graph_factory: GridGraphFactory | None = None,
        stepper_types: Sequence[type[SearchStepper]] | None = None,
    ) -> None:
        self.graph_factory = graph_factory or GridGraphFactory()
        self.stepper_types = stepper_types or (
            BreadthFirstStepper,
            DepthFirstStepper,
            DijkstraStepper,
            RandomWalkStepper,
        )
        self.config: GraphConfig | None = None
        self.graph: GridGraph | None = None
        self.metadata: GenerationMetadata | None = None
        self.running = False
        self._seed_anchor = random.SystemRandom().randint(0, 10**9)
        self._steppers: dict[str, SearchStepper] = {}

    def generate_graph(self, config: GraphConfig) -> GridGraph:
        self.pause()
        self.config = config
        self.graph, self.metadata = self.graph_factory.build(config)
        self._seed_anchor = config.seed if config.seed is not None else self._seed_anchor + 97
        self._steppers = {}
        for index, stepper_type in enumerate(self.stepper_types):
            seed = self._seed_anchor + index
            self._steppers[stepper_type.algorithm_id] = stepper_type(self.graph, seed=seed)
        return self.graph

    def start(self) -> None:
        if self.graph is not None:
            self.running = True

    def pause(self) -> None:
        self.running = False

    def reset(self) -> None:
        self.pause()
        for stepper in self._steppers.values():
            stepper.reset()

    def step_all(self) -> dict[str, SearchSnapshot]:
        snapshots = {name: stepper.step() for name, stepper in self._steppers.items()}
        if snapshots and all(stepper.is_finished for stepper in self._steppers.values()):
            self.running = False
        return snapshots

    def snapshots(self) -> dict[str, SearchSnapshot]:
        return {name: stepper.snapshot() for name, stepper in self._steppers.items()}

    @property
    def steppers(self) -> dict[str, SearchStepper]:
        return dict(self._steppers)
