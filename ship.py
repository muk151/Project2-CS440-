from collections import deque
import random 

cell_position = tuple[int, int]
movements = [
    (-1, 0),  # up
    (1, 0),   # down
    (0, -1),  # left
    (0, 1)    # right
] 

def gridNeighbors(cell, dimensions=(10, 10)): # returns neighbors in grid

    row = cell[0]
    col = cell[1]
    neighbors = []

    for rowChange, colChange in movements:
        newRow = row + rowChange
        newCol = col + colChange
         
        if 0 <= newRow < dimensions[0] and 0 <= newCol < dimensions[1]:
            neighbors.append((newRow, newCol))
        
    return neighbors

class Ship: 
    def __init__(self, openCells, dimensions, shipSize):
        self.openCells = set(openCells)
        self.dimensions = dimensions
        self.shipSize = shipSize
        self.shipCells = []
    
    def inBounds(self, cell):
        row = cell[0]
        col = cell[1]
        rowIsValid = 0 <= row < self.dimensions[0]
        colIsValid = 0 <= col < self.dimensions[1]
        return rowIsValid and colIsValid # will return true if the cell is in bounds
    
    def neighbors(self, cell):
        return gridNeighbors(cell, self.dimensions) # returns the neighbors of a cell
    
    def openNeighbors(self, cell): # will only return the neighbors that are open
        result = []
        for neighbor in self.neighbors(cell):
            if neighbor in self.openCells:
                result.append(neighbor)
        return result 
    def isConnected(self, cells):
        cells = set(cells)  # Accept lists or sets and keep membership checks fast.
        if not cells:
            return False
        
        start = next(iter(cells))
        visited = {start}
        queue = deque([start])
        
        while queue:
            current = queue.popleft()
            
            for neighbor in self.openNeighbors(current):
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)  # Mark before queuing to avoid duplicates.
                    queue.append(neighbor)
        
        return len(visited) == len(cells)
    def shipPicture(self, fire, bot, button):
        completedRow = []

        for row in range(self.dimensions[0]):
            currRow = []
            for col in range(self.dimensions[1]):
                cell = (row, col)
                if cell in self.openCells:
                    symbol = "."  # open cell
                else:
                    symbol = "#" # closed cell
                
                if cell == button: # button
                    symbol = "X"
                if cell in fire: # fire
                    symbol = "F"
                if cell == bot: # bot
                    symbol = "B"
                currRow.append(symbol)
            completedRow.append(" ".join(currRow))
        return "\n".join(completedRow)

def openNeighborsCount(cell, openCells, dimensions): # will count the number of open neighbors a cell has
        count = 0
        for neighbor in gridNeighbors(cell, dimensions):
            if neighbor in openCells:
                count += 1
        return count
def findBlockedCellNeighbors(openCells, dimensions): # will find blocked cells that have only one open neighbor
        possibleOpenNeighbors = []
        for row in range(dimensions[0]):
            for col in range(dimensions[1]):
                cell = (row, col)
                blockedCell = cell not in openCells
                if blockedCell:
                    numOpenNeighbors = openNeighborsCount(cell, openCells, dimensions)
                    if numOpenNeighbors == 1:
                        possibleOpenNeighbors.append(cell)
        return possibleOpenNeighbors
def deadEndCells(openCells, dimensions): # will find all dead end cells in the ship that have only one open neighbor
        deadEndCells = []
        for cell in openCells:
            numOpenNeighbors = openNeighborsCount(cell, openCells, dimensions)
            if numOpenNeighbors == 1:
                deadEndCells.append(cell)
        return deadEndCells
def closedNeighbors(openCells, cell, dimensions): # will find all closed neighbors of a cell
        closedNeighbors = []
        for neighbor in gridNeighbors(cell, dimensions):
            if neighbor not in openCells:
                closedNeighbors.append(neighbor)
        return closedNeighbors
def generateShip(sizeOfShip, rng=None): # generates a ship with random open and closed cells and makes sure that the ship is connected and does not have any dead ends
        dimensions = (sizeOfShip, sizeOfShip)
        
        if rng is None:
            rng = random.Random()
        
        startRow = rng.randint(1, sizeOfShip - 2)
        startCol = rng.randint(1, sizeOfShip - 2)
        startCell = (startRow, startCol)
            
        openCells = {startCell}
        potentialCandidates = findBlockedCellNeighbors(openCells, dimensions)

        while len(potentialCandidates) > 0: 
            cellChosen = rng.choice(potentialCandidates)
            openCells.add(cellChosen)
            potentialCandidates = findBlockedCellNeighbors(openCells, dimensions)

            
        currentDeadEndCells = deadEndCells(openCells, dimensions)
        originalDeadEndCells = len(currentDeadEndCells)
        maxDeadEndCells = originalDeadEndCells / 2

        while len(currentDeadEndCells) > maxDeadEndCells:
            deadEndCellsAllowed = []

            for deadEndCell in currentDeadEndCells:
                adjacentNeighbors = closedNeighbors(openCells, deadEndCell, dimensions)
                if len(adjacentNeighbors) > 0:
                    deadEndCellsAllowed.append(deadEndCell)
                
            if len(deadEndCellsAllowed) == 0:
                    break
                
            deadEndCellChosen = rng.choice(deadEndCellsAllowed)
            adjacentNeighbors = closedNeighbors(openCells, deadEndCellChosen, dimensions)
            cellToBeOpened = rng.choice(sorted(adjacentNeighbors))
            openCells.add(cellToBeOpened)
            currentDeadEndCells = deadEndCells(openCells, dimensions)
        
        ship = Ship(openCells, dimensions, sizeOfShip)

        

        return ship
    
def chooseInitialPos(ship, rng=None): # chooses the initial positions for the bot, button, and fire in the ship
        if rng is None:
            rng = random.Random()
        
        positionPossibilities = sorted(ship.openCells)
        positionChosen = rng.sample(positionPossibilities, 3) 

        botPosition = positionChosen[0]
        buttonPosition = positionChosen[1]
        firePosition = positionChosen[2]
        return botPosition, buttonPosition, firePosition 

def main(): # generates a ship and chooses initial positions for the bot, button, and fire and then prints the ship with the initial positions
     rng = random.Random()
     ship = generateShip(10, rng)

     bot, button, fire = chooseInitialPos(ship, rng)

     print(ship.shipPicture({fire}, bot, button))
     print()

if __name__ == "__main__":
        main()