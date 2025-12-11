import random
import math
from collections import Counter, defaultdict
import variants as v

def CreateRoles(N, E):
    """
    Create a list of roles for N players with E evil (including 1 Demon) 
    and Outsiders based on the player count. The rest are Good.
    """
    outsider_pattern = [1, 2, 0]
    outsider_count = outsider_pattern[(N - 8) % 3] if N >= 7 else 0

    num_good = N - E - outsider_count

    roles = ["Demon"] + ["Minion"] * (E - 1) + ["Outsider"] * outsider_count + ["Good"] * num_good
    return roles


def Experiment(roles, N,E, G=10000, seed=6767):
    rng = random.Random(seed)
    results = []
    for i in range(G):
        result = v.Game(
            roles=roles,
            rng=rng
        )
        results.append(result)

    wins = Counter(r["winner"] for r in results)
    erate = wins["Evil"] / G
    se = math.sqrt(erate * (1 - erate) / G)
    ci95 = (erate - 1.96*se, erate + 1.96*se)

    dayswin = defaultdict(list)
    for r in results:
        dayswin[r["winner"]].append(r["num_days"])

    def mean(x):
        return round(sum(x)/len(x),5) if x else None

    summary = {
        "Games": G,
        "# Players": N,
        "# Minions": E-1,
        "% Evil Win": erate,
        "STD-ERROR": round(se,5),
        "ConInt95": tuple(round(x,5) for x in ci95),
        "Avg Days": mean([r["num_days"] for r in results]),
        "Avg Days|Evil Win": mean(dayswin["Evil"]),
        "Avg Days|Good Win": mean(dayswin["Good"]),
        "wins": dict(wins)
    }
    return summary, results