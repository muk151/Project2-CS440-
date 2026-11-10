# detects behavior for Type A and Type B bots 
import math 

class detector: 
    def __init__(self, detectorType, k=2, alpha= 0.1): 
        self.detectorType = detectorType 
        self.k = k 
        self.alpha = alpha
        self.probabilityCache = {}
    def inSquare(self, locatorPos, cell): # returns True if the cell is within the square of side length 2k+1 centered at locatorPos
        rowDist = abs(locatorPos[0] - cell[0])
        colDist = abs(locatorPos[1] - cell[1])
        return rowDist <= self.k and colDist <= self.k
    def probDetails(self, locatorPos, cell): # returns the prob of a ping, prob of no ping, and entropy of the reading for a given locatorPos and cell which will cache results for efficiency
        if locatorPos in cell:
            return 0.0, 0.0, 0.0
        rowDist = abs(locatorPos[0] - cell[0])
        colDist = abs(locatorPos[1] - cell[1])
        key = (rowDist, colDist)
        if key not in self.probabilityCache: 
            dist = math.hypot(rowDist, colDist)
            expo = -(self.alpha) * (dist - 1)
            pingProb = math.exp(expo)
            noPingProb = 1 - pingProb
            readingEntropy = 0.0
            for prob in (pingProb, noPingProb):
                if prob > 0:
                    readingEntropy -= prob * math.log(prob)
            self.probabilityCache[key] = (pingProb, noPingProb, readingEntropy)
        return self.probabilityCache[key]
    def pingProb(self, locatorPos, cell): # returns ping prob for a given locatorPos and cell 
        if self.detectorType == "A":
            if locatorPos == cell:
                return 0.0
            return float(self.inSquare(locatorPos, cell))
        return self.probDetails(locatorPos, cell)[0]
    def sense(self, locatorPos, lostPos, rng): # returns the reading for a given locatorPos and lostPos and uses rng to randomize the result
        if locatorPos == lostPos:
            return "Found"
        if self.detectorType == "A":
            if self.inSquare(locatorPos, lostPos):
                return "Ping"
            return "No Ping"
        if rng.random() < self.pingProb(locatorPos, lostPos):
            return "Ping"
        return "No Ping"