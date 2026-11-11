"""Question 6: choose informative detector locations when movement is free.

Requires NumPy for scoring all sensing locations efficiently on larger ships.
"""

import numpy as np

from Bot1 import BaselineA
from Bot3 import BaselineB


def entropyTerms(probabilities):
    # each outcome contributes -p * log2(p), with zero contribution when p is zero
    terms = np.zeros_like(probabilities, dtype=float)
    positive = probabilities > 0
    terms[positive] = -probabilities[positive] * np.log2(probabilities[positive])
    return terms


class _InformationSearch:
    def prepareSensor(self):
        # this model uses ship geometry and hypothetical bot locations only
        self.moveCost = 0
        self.cells = sorted(self.ship.openCells)
        coordinates = np.array(self.cells)
        offsets = coordinates[:, None, :] - coordinates[None, :, :]
        if self.detector.detectorType == "A":
            self.ping = (np.max(np.abs(offsets), axis=2) <= self.detector.k).astype(float)
            self.noPing = 1 - self.ping
        else:
            distances = np.sqrt(np.sum(offsets ** 2, axis=2))
            # same-cell sensing returns Found, so avoid evaluating its exponential
            np.fill_diagonal(distances, 1)
            logPing = -self.detector.alpha * (distances - 1)
            self.ping = np.exp(logPing)
            self.noPing = -np.expm1(logPing)
        np.fill_diagonal(self.ping, 0)
        np.fill_diagonal(self.noPing, 0)
        self.sensorEntropy = entropyTerms(self.ping) + entropyTerms(self.noPing)
        self.lastSense = None
        self.samePositionReadings = 0

    def chooseTarget(self, distances):
        # retain the inherited belief updates, then predict readings at every location
        if self.detector.detectorType == "A":
            belief = np.array([float(cell in self.possibleLocations) for cell in self.cells])
        else:
            probabilities = self.probabilities
            belief = np.array([probabilities.get(cell, 0) for cell in self.cells])
        belief /= belief.sum()
        ping = self.ping @ belief
        noPing = self.noPing @ belief
        # information gain subtracts sensor noise from the entropy of the three outcomes
        gain = (entropyTerms(belief) + entropyTerms(ping) + entropyTerms(noPing)
                - self.sensorEntropy @ belief)
        gain = np.maximum(gain, 0)

        # after three readings in one place, check a most-probable cell to make progress
        self.samePositionReadings = self.samePositionReadings + 1 if self.lastSense == self.position else 1
        self.lastSense = self.position
        if self.samePositionReadings >= 3 or gain.max() < 1e-10:
            candidates = np.flatnonzero(belief == belief.max())
        else:
            candidates = np.flatnonzero(np.isclose(gain, gain.max(), rtol=1e-10, atol=1e-12))
        # movement only breaks ties here, since it contributes zero to the cost
        nearest = min(distances[self.cells[i]] for i in candidates)
        ties = [self.cells[i] for i in candidates if distances[self.cells[i]] == nearest]
        return self.rng.choice(ties)


class FreeMovementA(_InformationSearch, BaselineA):
    def __init__(self, ship, locatorPos, k=2, rng=None):
        # reuse type a's deterministic update and replace its target choice
        super().__init__(ship, locatorPos, k=k, rng=rng)
        self.prepareSensor()


class FreeMovementB(_InformationSearch, BaselineB):
    def __init__(self, ship, locatorPos, alpha=0.1, rng=None):
        # reuse type b's Bayesian update and replace its target choice
        super().__init__(ship, locatorPos, alpha=alpha, rng=rng)
        self.prepareSensor()
