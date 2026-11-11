# Runs the bots and prints results for Type A and Type B
import random
from statistics import mean
from ship import generateShip
from Bot1 import BaselineA
from Bot2 import improvedA
from Bot3 import BaselineB
from Bot4 import ImprovedB

shipSize = 15
trials = 30
singleK = 2
kValues = [0, 1, 2, 3, 4, 6, 8, 10, 14]
alpha = 0.1
alphaValues = [0.05, 0.1, 0.2, 0.3, 0.4, 0.6, 1.0]
seed = 0


def makeSearch(seed): # returns ship, start position, lost position for a specific seed 
    setup = random.Random(seed)
    ship = generateShip(shipSize, setup)
    start, lost = setup.sample(sorted(ship.openCells), 2)
    return ship, start, lost
def runEachBot(): # runs a search for each bot and will print the results 
    ship, start, lost = makeSearch(seed)
    print("One search on the same ship:") 
    print("Start:", start, "LostBot:", lost) # prints start position and lost position for the search 
    bots = [("Bot 1", BaselineA, {"k": singleK}), ("Bot 2", improvedA, {"k": singleK}),("Bot 3", BaselineB, {"alpha": alpha}),("Bot 4", ImprovedB, {"alpha": alpha}),] # list of bots to run with those specific settings
    for name, botClass, settings in bots:
        bot = botClass(ship, start, rng=random.Random(seed + 1000), **settings)
        result = bot.run(lost)
        print(name, "moves:", result.moves,
              "detector calls:", result.detectorActions,
              "cost:", result.cost)
def compareKValues(): # compares the average discovery cost for Type A bots that are over a range of specific k values and will print the results 
    print("\nAverage Type A discovery cost over", trials, "trials:")
    for k in kValues:
        baselineCosts = []
        improvedCosts = []
        for seed in range(trials):
            ship, start, lost = makeSearch(seed)
            bot1 = BaselineA(ship, start, k=k,rng=random.Random(seed + 1000)) # creates an new instance for the baseline A bot with a specific k value and an RNG that is seeded with the trial number (+ 1000) 
            bot2 = improvedA(ship, start, k=k,rng=random.Random(seed + 1000)) # creates an new instance for the improved A bot with a specific k value and an RNG that is seeded with the trial number (+ 1000)
            baselineCosts.append(bot1.run(lost).cost)
            improvedCosts.append(bot2.run(lost).cost)

        print(f"k={k:2d}  Bot 1={mean(baselineCosts):6.2f}" # prints the average discovery cost for the baseline A bot and the improved A bot for a specific k value
              f"  Bot 2={mean(improvedCosts):6.2f}")
def compareAlphaValues(): # compares the average discovery cost for Type B bots that are over a range of specific alpha values and will print those results 
    print("\nAverage Type B discovery cost over", trials, "trials:")
    for alpha in alphaValues:
        baselineCosts = []
        improvedCosts = []

        for seed in range(trials):
            ship, start, lost = makeSearch(seed)
            bot3 = BaselineB(ship, start, alpha=alpha,rng=random.Random(seed + 1000)) # creates an new instance for the baseline B bot with a specific alpha value and an RNG that is seeded with the trial number (+ 1000)
            bot4 = ImprovedB(ship, start, alpha=alpha,rng=random.Random(seed + 1000)) # creates an new instance for the improved B bot with a specific alpha value and an RNG that is seeded with the trial number (+ 1000)
            baselineCosts.append(bot3.run(lost).cost)
            improvedCosts.append(bot4.run(lost).cost)

        print(f"alpha={alpha:4.2f}  Bot 3={mean(baselineCosts):6.2f}"
              f"  Bot 4={mean(improvedCosts):6.2f}")
if __name__ == "__main__": # runs the bots and compares the average discovery cost for Type A and Type B bots over a range of specific k and alpha values
    runEachBot()
    compareKValues()
    compareAlphaValues()
