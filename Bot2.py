# improved version of A (scan and narrow algorithm)
from Bot1 import BaselineA
from detectors import detector

class improvedA(BaselineA):
    def __init__(self, ship, locatorPos, k=2, rng=None):
        super().__init__(ship, locatorPos, detector("A", k=k), rng)
        self.possibleCells = set(ship.openCells)
        self.hasReceivedPing = False

    def updateKnowledge(self, reading):
       remainingCells = set()
       for cell in self.possibleCells:
            inside = self.detector.inSquare(self.position, cell)
            if (reading == "Ping" and inside) or (reading == "No Ping" and not inside):
                remainingCells.add(cell)
       self.possibleCells = remainingCells
       if reading == "Ping":
            self.hasReceivedPing = True

    def chooseTarget(self, distances):
        if self.hasReceivedPing:
            nearest = min(distances[cell] for cell in self.possibleCells)
            choices = []
            for cell in sorted(self.possibleCells):
                if distances[cell] == nearest:
                    choices.append(cell)
            return self.rng.choice(choices)

        bestScore = -1
        choices = []
        for destination in sorted(self.ship.openCells):
            covered = 0
            for cell in self.possibleCells:
                if self.detector.inSquare(destination, cell):
                    covered += 1
            score = covered / (distances[destination] + 0.5)
            if score > bestScore:
                bestScore = score
                choices = [destination]
            elif score == bestScore:
                choices.append(destination)
        return self.rng.choice(choices)
