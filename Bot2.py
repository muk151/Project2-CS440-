# improved version of A (scan and narrow algorithm)
from Bot1 import BaselineA

class improvedA(BaselineA):
    def __init__(self, ship, locatorPos, k=2, rng=None):
        super().__init__(ship, locatorPos, k=k, rng=rng)
        self.hasReceivedPing = False

    @property
    def possibleCells(self):
        return self.possibleLocations

    def updateKnowledge(self, reading):
       super().updateKnowledge(reading)
       if reading == "Ping":
            self.hasReceivedPing = True

    def chooseTarget(self, distances):
        if self.hasReceivedPing:
            return super().chooseTarget(distances)
        numCandidates = len(self.possibleLocations)
        bestScore = -1.0
        choices = []
        for destination in sorted(self.ship.openCells):
            foundCount = int(destination in self.possibleLocations)
            pingCount = sum(
                cell != destination and self.detector.inSquare(destination, cell)
                for cell in self.possibleLocations
            )
            noPingCount = numCandidates - foundCount - pingCount
            expectedRemaining = (pingCount ** 2 + noPingCount ** 2) / numCandidates
            expectedEliminated = numCandidates - expectedRemaining
            score = expectedEliminated / (distances[destination] + 0.5)
            if score > bestScore:
                bestScore = score
                choices = [destination]
            elif score == bestScore:
                choices.append(destination)
        return self.rng.choice(choices)