import pandas as pd
from experiment import Experiment, CreateRoles
import matplotlib.pyplot as plt
import numpy as np
import pprint
import itertools
import os

CSV_FILE = "results.csv"

# ---------------------------
#  Role modifier utilities
# ---------------------------

def replace_first(r, old, new):
    if old in r:
        r[r.index(old)] = new
    return r

ROLE_MODIFIERS = {
    "PoppyGrower": lambda r: replace_first(r, "Good", "PoppyGrower"),
    "ScarletWoman": lambda r: replace_first(r, "Minion", "ScarletWoman"),
    "Assassin": lambda r: replace_first(r, "Minion", "Assassin"),
    "Godfather": lambda r: replace_first(r, "Minion", "Godfather"),
    "DA": lambda r: replace_first(r, "Minion", "DA"),
    "Boomdandy": lambda r: replace_first(r, "Minion", "Boomdandy"),
    "Goblin": lambda r: replace_first(r, "Minion", "Goblin"),
    "Witch": lambda r: replace_first(r, "Minion", "Witch"),
    "Saint": lambda r: replace_first(r, "Outsider", "Saint"),
    "Klutz": lambda r: replace_first(r, "Outsider", "Klutz")
}

# ---------------------------
#  Experiment runner
# ---------------------------

def run_experiments(experiment_role_lists):
    """
    experiment_role_lists = [
        ["ScarletWoman"],
        ["Assassin"],
        ["Goblin", "Witch"],
        [],
    ]
    Returns: dict: name -> list of summaries (1 per player count)
    """

    results_by_experiment = {}
    experiment_defs = []

    for roles in experiment_role_lists:
        name = "Normal" if roles == [] else "+".join(roles)
        experiment_defs.append({"name": name, "roles_to_add": roles})

    print("EXPERIMENTS being run:")
    for e in experiment_defs:
        print("  ", e["name"])
    print("Total:", len(experiment_defs))

    for exp in experiment_defs:
        exp_array = []
        for N in range(7, 15):
            E = (N - 1) // 3

            roles = CreateRoles(N, E)
            for role_name in exp["roles_to_add"]:
                roles = ROLE_MODIFIERS[role_name](roles)

            summary, _ = Experiment(roles, N, E)
            exp_array.append(summary)
            pprint.pprint(summary)

        results_by_experiment[exp["name"]] = exp_array

    return results_by_experiment

def combos_of_three(role_list):
    return list(list(x) for x in itertools.combinations(role_list, 3))

def plot_by_playercount(results_by_experiment):
    plt.figure(figsize=(10,6))

    experiment_names = list(results_by_experiment.keys())
    base = results_by_experiment[experiment_names[0]]
    x = [x['# Players'] for x in base]

    width = 0.8 / len(experiment_names)
    offsets = [(i - (len(experiment_names)-1)/2)*width for i in range(len(experiment_names))]

    for idx, name in enumerate(experiment_names):
        v = [s['% Evil Win'] for s in results_by_experiment[name]]
        plt.bar([xi + offsets[idx] for xi in x], v, width, label=name)

    plt.axhline(0.5, color='black', linestyle='--', linewidth=1)
    plt.ylim(0, 1)
    plt.xlabel('Player Count')
    plt.ylabel('Evil Win%')
    plt.title('Evil Win Percentage by Player Count (Random Execution)')
    plt.legend()
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def plot_by_experiment_average(results_by_experiment):
    names = []
    avgs = []

    for name, summaries in results_by_experiment.items():
        values = [s['% Evil Win'] for s in summaries]
        names.append(name)
        avgs.append(np.mean(values))

    plt.figure(figsize=(10,5))
    plt.bar(names, avgs)
    plt.axhline(0.5, color='black', linestyle='--', linewidth=1)
    plt.ylim(0,1)
    plt.ylabel("Avg Evil Win Rate")
    plt.title("Average Evil Win Rate Across All Player Counts")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()

def save_experiment_to_csv(all_roles, summary_dict):
    """
    Save experiment result to CSV, with first column 'Roles' (semicolon-separated)
    and the rest of the columns from summary_dict.
    """
    columns = ["Roles", "Games", "# Players", "# Minions", "% Evil Win", 
               "STD-ERROR", "ConInt95", "Avg Days", "Avg Days|Evil Win", "Avg Days|Good Win"]

    role_string = ";".join(all_roles)

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, sep=";")
        for col in columns:
            if col not in df.columns:
                df[col] = None
    else:
        df = pd.DataFrame(columns=columns)

    if (df["Roles"] == role_string).any():
        print(f"Experiment already exists for {role_string}. Skipping.")
        return

    row_data = [role_string] + [summary_dict.get(col, None) for col in columns[1:]]
    df_new = pd.DataFrame([row_data], columns=columns)

    df = pd.concat([df, df_new], ignore_index=True)
    df.to_csv(CSV_FILE, sep=";", index=False)

# Example code with all combos of existing minion roles + outsider variations (with/without PoppyGrower)
role_sets = []
MINION_ROLES = [r for r in ROLE_MODIFIERS.keys() if r not in ["PoppyGrower", "Saint", "Klutz"]]
minion_combos = list(itertools.combinations(MINION_ROLES, 3))

EXTRA_OPTIONS = [
    [],  # minions + Outsider placeholder
    ["Klutz"],
    ["Saint"],
    ["Saint", "Klutz"]
]

for combo in minion_combos:
    for extra in EXTRA_OPTIONS:
        role_sets.append(list(combo) + extra)
        role_sets.append(list(combo) + extra + ["PoppyGrower"])

results = run_experiments(role_sets)

for exp_name, summaries in results.items():
    roles_in_exp = exp_name.split("+") if exp_name != "Normal" else []
    for summary in summaries:
        N = summary['# Players']
        E = (N - 1) // 3
        all_roles = CreateRoles(N, E)
        for role_name in roles_in_exp:
            all_roles = ROLE_MODIFIERS.get(role_name, lambda r: r)(all_roles)

        save_experiment_to_csv(all_roles, summary)


plot_by_playercount(results)            # original plot
plot_by_experiment_average(results)     # new averaged plot
