"""Shared movement and action accounting for the two baseline bots."""

from collections import deque
from dataclasses import dataclass
import random


@dataclass(frozen=True)
class SearchResult:
    # keep the final location and action counts together for easy comparison
    position: tuple[int, int]
    moves: int
    detectorActions: int

    @property
    def cost(self):
        # a detector reading costs half as much as moving one cell
        return self.moves + 0.5 * self.detectorActions


class BaselineBot:
    def __init__(self, ship, locatorPos, sensor, rng=None):
        # both bots start with the same movement setup and action counters
        if locatorPos not in ship.openCells:
            raise ValueError("The locator must start in an open cell.")
        self.ship = ship
        self.position = locatorPos
        self.detector = sensor
        self.rng = rng if rng is not None else random.Random()
        self.moves = 0
        self.detectorActions = 0
        # BFS as a connectivity check
        distances, _ = self.shortestPaths()
        if len(distances) != len(ship.openCells):
            raise ValueError("All open cells must be connected.")

    def shortestPaths(self):
        """Standard breadth-first search (BFS) over the ship's open cells."""
        # distances count steps, and parents remember how we reached each cell
        distances = {self.position: 0}
        parents = {self.position: None}
        queue = deque([self.position])
        while queue:
            current = queue.popleft()
            # only look at adjacent open cells, since we can't walk through walls
            for neighbor in self.ship.openNeighbors(current):
                if neighbor not in distances:
                    # record each cell once
                    distances[neighbor] = distances[current] + 1
                    parents[neighbor] = current
                    queue.append(neighbor)
        return distances, parents

    def run(self, lostPos):
        """Run one search. Only the detector receives the true LostBot position."""
        # check the search setup before taking any actions
        if lostPos not in self.ship.openCells:
            raise ValueError("LostBot must be in an open cell.")
        if self.detectorActions:
            raise ValueError("Create a new bot for each search.")
        # this is the assignment's sense-update-move loop, with BFS for route planning
        while True:
            reading = self.detector.sense(self.position, lostPos, self.rng)
            self.detectorActions += 1
            if reading == "Found":
                return SearchResult(self.position, self.moves, self.detectorActions)

            # let bot one or bot three update its beliefs and pick a target
            self.updateKnowledge(reading)
            distances, parents = self.shortestPaths()
            target = self.chooseTarget(distances)
            path = []
            current = target
            # standard BFS path reconstruction: follow parent links back to the start
            # this just rebuilds the chosen path; it isn't a separate DFS search
            while current != self.position:
                path.append(current)
                current = parents[current]
            # reverse that route and walk it one step at a time before sensing again
            for cell in reversed(path):
                self.position = cell
                self.moves += 1

    def updateKnowledge(self, reading):
        # the bot classes fill this in because their detector updates are different
        raise NotImplementedError

    def chooseTarget(self, distances):
        # the bot classes also supply their own rules for choosing where to go
        raise NotImplementedError
