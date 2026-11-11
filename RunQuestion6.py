"""Compare the baselines, previous strategies, and free-movement strategies.

Example: python RunQuestion6.py --size 30 --trials 100
Requires NumPy. Results are saved under output/question6.
"""

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
from pathlib import Path
import random
from statistics import mean
import time

import numpy as np

from Bot1 import BaselineA
from Bot2 import improvedA
from Bot3 import BaselineB
from Bot4 import ImprovedB
from FreeMovement import FreeMovementA, FreeMovementB
from ship import generateShip


class _FastPreviousA(improvedA):
    def prepareCoverage(self):
        # cache the same square membership counts used by the revised bot 2
        self.cells = sorted(self.ship.openCells)
        coordinates = np.array(self.cells)
        offsets = coordinates[:, None, :] - coordinates[None, :, :]
        self.coverage = (np.max(np.abs(offsets), axis=2) <= self.detector.k).astype(np.int64)

    def chooseTarget(self, distances):
        # keep bot 2's narrowing phase and speed up its scan without changing the rule
        if self.hasReceivedPing:
            return super().chooseTarget(distances)
        found = np.array([cell in self.possibleLocations for cell in self.cells], dtype=np.int64)
        count = len(self.possibleLocations)
        ping = self.coverage @ found - found
        noPing = count - found - ping
        eliminated = count - (ping ** 2 + noPing ** 2) / count
        scores = eliminated / np.array([distances[cell] + 0.5 for cell in self.cells])
        ties = [self.cells[i] for i in np.flatnonzero(scores == scores.max())]
        return self.rng.choice(ties)


def runTrial(settings):
    # only the environment gets the sampled true LostBot location
    size, trial, alphas = settings
    setup = random.Random(trial)
    ship = generateShip(size, setup)
    start, lost = setup.sample(sorted(ship.openCells), 2)
    rows = []
    for kind, parameters in [('A', range(size)), ('B', alphas)]:
        # retune each policy for detector-only cost across the same settings
        for parameter in parameters:
            if kind == 'A':
                bots = [BaselineA(ship, start, k=parameter, rng=random.Random(trial + 1000)),
                        _FastPreviousA(ship, start, k=parameter, rng=random.Random(trial + 1000)),
                        FreeMovementA(ship, start, k=parameter, rng=random.Random(trial + 1000))]
                bots[1].prepareCoverage()
            else:
                bots = [BaselineB(ship, start, alpha=parameter, rng=random.Random(trial + 1000)),
                        ImprovedB(ship, start, alpha=parameter, rng=random.Random(trial + 1000)),
                        FreeMovementB(ship, start, alpha=parameter, rng=random.Random(trial + 1000))]
            for policy, bot in zip(['baseline', 'previous', 'free'], bots):
                result = bot.run(lost)
                assert result.position == lost
                assert result.detectorActions <= 4 * len(ship.openCells)
                # the previous policies retain their target rules, with movement re-scored as free
                freeCost = 0.5 * result.detectorActions
                if policy == 'free':
                    assert result.cost == freeCost
                rows.append(dict(size=size, trial=trial, kind=kind, parameter=parameter,
                                 policy=policy, moves=result.moves,
                                 readings=result.detectorActions, cost=freeCost))
    return rows


def main():
    # keep the experiment reproducible with the same seeds as the group writeup
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', type=int, default=30)
    parser.add_argument('--trials', type=int, default=100)
    parser.add_argument('--workers', type=int, default=3)
    args = parser.parse_args()
    if args.size < 3 or args.trials < 1 or args.workers < 1:
        parser.error('size must be at least 3; trials and workers must be positive')
    alphas = [0.01, 0.03, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 1.0]
    output = Path(__file__).resolve().parent / 'output/question6'
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.monotonic()
    fields = ['size', 'trial', 'kind', 'parameter', 'policy', 'moves', 'readings', 'cost']
    with (output / f'size{args.size}.csv').open('w', newline='') as f, ProcessPoolExecutor(max_workers=args.workers) as pool:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        jobs = [pool.submit(runTrial, (args.size, trial, alphas)) for trial in range(args.trials)]
        for finished, job in enumerate(as_completed(jobs), 1):
            batch = job.result()
            rows.extend(batch)
            writer.writerows(batch)
            f.flush()
            print(f'{finished}/{args.trials} ships finished in {time.monotonic() - started:.1f}s', flush=True)
    summary = []
    for kind, parameters in [('A', list(range(args.size))), ('B', alphas)]:
        # choose the best tested parameter independently for each policy
        for policy in ['baseline', 'previous', 'free']:
            means = {parameter: mean(r['cost'] for r in rows
                                    if (r['kind'], r['policy'], r['parameter']) == (kind, policy, parameter))
                     for parameter in parameters}
            best = min(means, key=lambda p: (means[p], p))
            summary.append(dict(kind=kind, policy=policy, parameter=best,
                                meanCost=means[best], meanReadings=2 * means[best]))
    report = dict(size=args.size, trials=args.trials, alphas=alphas,
                  kValues=list(range(args.size)), results=summary)
    (output / f'size{args.size}_summary.json').write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
