"""Baseline Type B"""

import math

from baseline import BaselineBot
from detectors import detector


class BaselineB(BaselineBot):
    def __init__(self, ship, locatorPos, alpha=0.1, rng=None):
        # check the sensitivity before setting up the detector
        if not math.isfinite(alpha) or alpha <= 0:
            raise ValueError("alpha must be finite and positive.")
        super().__init__(ship, locatorPos, detector("B", alpha=alpha), rng)
        # logs keep tiny beliefs from rounding to zero during updates
        initial = -math.log(len(ship.openCells))
        # give every open cell the same starting probability
        self.logProbabilities = {cell: initial for cell in ship.openCells}

    @property
    def probabilities(self):
        # convert each stored log value back to a regular probability for inspection
        return {cell: math.exp(value)
                for cell, value in self.logProbabilities.items()}

    def updateKnowledge(self, reading):
        # use the reading to update each cell's belief with bayes' rule
        if reading not in ("Ping", "No Ping"):
            raise ValueError("Expected Ping or No Ping.")
        updated = {}
        # combine each old belief with how likely this reading is at that cell
        for cell, prior in self.logProbabilities.items():
            if cell == self.position:
                # we'd have gotten found if the lost bot were here
                continue
            distance = math.hypot(cell[0] - self.position[0],
                                  cell[1] - self.position[1])
            logPing = -self.detector.alpha * (distance - 1)
            if reading == "Ping":
                logLikelihood = logPing
            else:
                # expm1 keeps no ping accurate when ping is very close to 1
                noPing = -math.expm1(logPing)
                if noPing == 0:
                    continue
                logLikelihood = math.log(noPing)
            # adding logs is the same as multiplying the original probabilities
            updated[cell] = prior + logLikelihood

        if not updated:
            raise ValueError("Detector reading contradicts all possible locations.")
        largest = max(updated.values())
        # shift by the largest log value so the normalization stays stable
        logTotal = math.log(sum(math.exp(value - largest)
                                for value in updated.values()))
        # normalize all the remaining beliefs so their probabilities add up to 1
        self.logProbabilities = {
            cell: (value - largest) - logTotal
            for cell, value in updated.items()
        }

    def chooseTarget(self, distances):
        # first keep only the cells with the highest belief
        highest = max(self.logProbabilities.values())
        ties = [cell for cell, value in self.logProbabilities.items()
                if value == highest]
        # among those cells, prefer the closest ones and break any leftover tie randomly
        nearest = min(distances[cell] for cell in ties)
        return self.rng.choice(sorted(cell for cell in ties
                                      if distances[cell] == nearest))
