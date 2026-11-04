# improved version of B
# B but with a greedy probability-per-cost target rule.

import math

from Bot3 import BaselineB


class ImprovedB(BaselineB):
    def __init__(self, ship, locatorPos, alpha=0.1, rng=None, moveCost=1):
        # use 1 for normal movement cost, or 0 for the free movement experiment
        if not math.isfinite(moveCost) or moveCost < 0:
            raise ValueError("moveCost must be finite and nonnegative.")
        super().__init__(ship, locatorPos, alpha=alpha, rng=rng)
        self.moveCost = moveCost

    def chooseTarget(self, distances):
        # with free movement, probability per cost reduces to baseline b's rule
        if self.moveCost == 0:
            return super().chooseTarget(distances)

        # greedy score: probability / (BFS travel cost + one detector reading)
        # compare logs so even tiny probabilities can still be ranked accurately
        scores = {
            cell: belief - math.log(self.moveCost * distances[cell] + 0.5)
            for cell, belief in self.logProbabilities.items()
        }
        best = max(scores.values())
        ties = [cell for cell, score in scores.items() if score == best]
        # prefer the shorter route on a score tie, then choose randomly
        nearest = min(distances[cell] for cell in ties)
        return self.rng.choice(sorted(cell for cell in ties
                                      if distances[cell] == nearest))

    @property
    def totalCost(self):
        # include the selected movement cost; run()'s result.cost uses the default cost
        return self.moveCost * self.moves + 0.5 * self.detectorActions
