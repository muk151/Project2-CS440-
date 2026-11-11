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


def make_search(seed): # returns ship, start position, lost position for a specific seed 
    setup = random.Random(seed)
    ship = generateShip(shipSize, setup)
    start, lost = setup.sample(sorted(ship.openCells), 2)
    return ship, start, lost
def run_each_bot(): # runs a search for each bot and will print the results 
    ship, start, lost = make_search(seed)
    print("One search on the same ship:") 
    print("Start:", start, "LostBot:", lost) # prints start position and lost position for the search 
    bots = [("Bot 1", BaselineA, {"k": singleK}), ("Bot 2", improvedA, {"k": singleK}),("Bot 3", BaselineB, {"alpha": alpha}),("Bot 4", ImprovedB, {"alpha": alpha}),] # list of bots to run with those specific settings
    for name, bot_class, settings in bots:
        bot = bot_class(ship, start, rng=random.Random(seed + 1000), **settings)
        result = bot.run(lost)
        print(name, "moves:", result.moves,
              "detector calls:", result.detectorActions,
              "cost:", result.cost)
def compare_k_values(): # compares the average discovery cost for Type A bots that are over a range of specific k values and will print the results 
    print("\nAverage Type A discovery cost over", trials, "trials:")
    for k in kValues:
        baseline_costs = []
        improved_costs = []
        for seed in range(trials):
            ship, start, lost = make_search(seed)
            bot1 = BaselineA(ship, start, k=k,rng=random.Random(seed + 1000)) # creates an new instance for the baseline A bot with a specific k value and an RNG that is seeded with the trial number (+ 1000) 
            bot2 = improvedA(ship, start, k=k,rng=random.Random(seed + 1000)) # creates an new instance for the improved A bot with a specific k value and an RNG that is seeded with the trial number (+ 1000)
            baseline_costs.append(bot1.run(lost).cost)
            improved_costs.append(bot2.run(lost).cost)

        print(f"k={k:2d}  Bot 1={mean(baseline_costs):6.2f}" # prints the average discovery cost for the baseline A bot and the improved A bot for a specific k value
              f"  Bot 2={mean(improved_costs):6.2f}")
def compare_alpha_values(): # compares the average discovery cost for Type B bots that are over a range of specific alpha values and will print those results 
    print("\nAverage Type B discovery cost over", trials, "trials:")
    for alpha in alphaValues:
        baseline_costs = []
        improved_costs = []

        for seed in range(trials):
            ship, start, lost = make_search(seed)
            bot3 = BaselineB(ship, start, alpha=alpha,rng=random.Random(seed + 1000)) # creates an new instance for the baseline B bot with a specific alpha value and an RNG that is seeded with the trial number (+ 1000)
            bot4 = ImprovedB(ship, start, alpha=alpha,rng=random.Random(seed + 1000)) # creates an new instance for the improved B bot with a specific alpha value and an RNG that is seeded with the trial number (+ 1000)
            baseline_costs.append(bot3.run(lost).cost)
            improved_costs.append(bot4.run(lost).cost)

        print(f"alpha={alpha:4.2f}  Bot 3={mean(baseline_costs):6.2f}"
              f"  Bot 4={mean(improved_costs):6.2f}")
if __name__ == "__main__": # runs the bots and compares the average discovery cost for Type A and Type B bots over a range of specific k and alpha values
    run_each_bot()
    compare_k_values()
    compare_alpha_values()
