"""Baseline Type A"""

from baseline import BaselineBot
from detectors import detector


class BaselineA(BaselineBot):
    def __init__(self, ship, locatorPos, k=2, rng=None):
        # start with every open cell as a possible location
        if not isinstance(k, int) or k < 0:
            raise ValueError("k must be a nonnegative integer.")
        super().__init__(ship, locatorPos, detector("A", k=k), rng)
        self.possibleLocations = set(ship.openCells)

    def updateKnowledge(self, reading):
        # keep only the cells that agree with this detector reading
        if reading not in ("Ping", "No Ping"):
            raise ValueError("Expected Ping or No Ping.")
        # no found reading means the bot isn't in our current cell either
        self.possibleLocations = {
            cell for cell in self.possibleLocations
            if cell != self.position
            and self.detector.inSquare(self.position, cell) == (reading == "Ping")
        }
        if not self.possibleLocations:
            raise ValueError("Detector reading contradicts all possible locations.")

    def chooseTarget(self, distances):
        # find the shortest travel distance among the remaining candidates
        nearest = min(distances[cell] for cell in self.possibleLocations)
        # collect all equally close cells so ties can be broken randomly
        ties = sorted(cell for cell in self.possibleLocations
                      if distances[cell] == nearest)
        return self.rng.choice(ties)
