# Blood-On-The-Clocktower-Random-Execution-Simulator
Monte Carlo simulator for random executions with different role setups.

## Use:
- Run setup.py first to create the csv (note that a results.csv with a lot of experiments already ran is provided in the repo so if you keep that file, you can skip this step). 
- Then in the bottom section of main.py you can change the experiments being ran and the graphs being created, by writing your own experiments.
- You can keep this line: results = run_experiments(role_sets), where role_sets is a list of different roles being used.

## Other potential options:
- You can also create a seperate document to just graph the already existing results in results.csv (this csv included a lot of experiments I already ran, so it is likely you're experiment already has data.
- You can also add new roles to try out by defining new classes and hooks in variants.py, however, due to difficult integration, this is not recommended.

## Roles:
### Demon
- Only the placeholder demon is supported in this version (kill once)
### Minion
- Assassin
- Godfather
- DA
- Boomdandy
- Goblin
- Witch
- Scarlet Woman
- Placeholder Minion (No ability evil player)
### Outsider
- Saint
- Klutz
- Placeholder Outsider (Same as normal townsfolk at this time)
### Townsfolk
- Poppy Grower
- Normal Townsfolk (No ability)

The matplotlib graphin algorithms were created by ChatGPT.
