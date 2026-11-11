# improved version of A (scan and narrow algorithm)
from Bot1 import BaselineA

class improvedA(BaselineA):
    def __init__(self, ship, locatorPos, k=2, rng=None): # initializes the improvedA bot with a ship, locator position, k value, and random number generator
        super().__init__(ship, locatorPos, k=k, rng=rng)
        self.hasReceivedPing = False

    @property
    def possibleCells(self): # returns the set of possible cells where the LostBot could be located
        return self.possibleLocations

    def updateKnowledge(self, reading): # updates the bot's knowledge based on the detector reading and sets hasReceivedPing to True if a ping is received
       super().updateKnowledge(reading)
       if reading == "Ping":
            self.hasReceivedPing = True

    def chooseTarget(self, distances): # chooses the next target cell based on the bot's knowledge and the distances to each cell
        if self.hasReceivedPing:
            return super().chooseTarget(distances) # if a ping has been received, use the baseline A bot's chooseTarget method to select the next target
        numCandidates = len(self.possibleLocations)
        bestScore = -1.0
        choices = []
        for destination in sorted(self.ship.openCells): 
            foundCount = int(destination in self.possibleLocations)
            pingCount = sum(cell != destination and self.detector.inSquare(destination, cell) for cell in self.possibleLocations) # counts the number of possible locations that would result in a ping if the bot were to move to the destination cell
            noPingCount = numCandidates - foundCount - pingCount # counts the number of possible locations that would not result in a ping if the bot were to move to the destination cell
            expectedRemaining = (pingCount ** 2 + noPingCount ** 2) / numCandidates # calculates the expected number of remaining possible locations after moving to the destination cell, based on the probabilities of receiving a ping or no ping
            expectedEliminated = numCandidates - expectedRemaining # calculates the expected number of possible locations that would be eliminated after moving to the destination cell
            score = expectedEliminated / (distances[destination] + 0.5) 
            if score > bestScore:
                bestScore = score
                choices = [destination]
            elif score == bestScore:
                choices.append(destination)
        return self.rng.choice(choices)