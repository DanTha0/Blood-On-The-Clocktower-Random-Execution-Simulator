import random

demon = None
a_poppy = False
player_roles = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

class Role:
    """Base class for roles; override hooks for special behavior."""
    def on_demon_killed(self, alive, player_roles, demon, day):
        """
        Called when the demon is executed.
        Return True if the game ends (Good wins), False otherwise.
        """
        return True

class ScarletWoman(Role): 
    def on_demon_killed(self, alive, player_roles, demon, day): 
        for p in alive: 
            if player_roles[p] == "ScarletWoman": 
                if (len(alive) > 4): 
                    alive.remove(p) 
                    alive.add(demon) 
                    return False 
                else: 
                    return True 
        return True

class PoppyGrower:
    def on_night_action(self, alive, player_roles, demon, rng):
        poppy_alive = any(player_roles[p] == "PoppyGrower" for p in alive)
        return "PoppyKill"

class Assassin:
    def __init__(self):
        self.used = False

    def on_night_action(self, alive, player_roles, demon, rng):
        if self.used:
            return False
        targets = getGoodtargets(alive, player_roles)
        if targets:
            target = rng.choice(targets)
            kill(alive, target, rng)
            self.used = True
            return True
        return False

class Godfather:
    def __init__(self):
        self.pending_kill = False
        self.kill_count = 0

    def setup(self, alive, player_roles):
        for i, role in enumerate(player_roles):
            if ALIGNMENTS[role] == 1 and role != "Outsider":
                player_roles[i] = "Outsider"
                break

    def on_player_executed(self, executed, alive, player_roles, rng):
        if player_roles[executed] == "Outsider":
            self.pending_kill = True

    def on_night_action(self, alive, player_roles, demon, rng):
        if not self.pending_kill:
            return False
        targets = getGoodtargets(alive, player_roles)
        if targets:
            target = rng.choice(targets)
            kill(alive, target, rng)
            self.kill_count += 1
        else:
            self.pending_kill = False
        return True

class DA:
    def __init__(self):
        self.target = None  # Player selected each night
        self.last_target = None  # Track previous night's target

    def on_night_action(self, alive, player_roles, demon, rng):
        global a_poppy
        if a_poppy == False:
            minion_candidates = [p for p in alive if ALIGNMENTS[player_roles[p]] == 0 and p != demon]
            first_minion = minion_candidates[0] if minion_candidates else None
            if self.last_target == demon:
                self.target = first_minion
            else:
                self.target = demon if demon in alive else first_minion
            
            if self.target is None:
                self.target = rng.choice([p for p in alive if p != self.last_target])

            self.last_target = self.target
            return False
        else:
            first_minion = rng.choice([p for p in alive if p != self.last_target])
            self.last_target = self.target
            return False
            
    def on_player_executed(self, executed, alive, player_roles, rng):
        if self.target is not None and executed == self.target:
            alive.add(executed)
            self.target = None
            return True
        return False

class Boomdandy:
    def on_player_executed(self, executed, alive, player_roles, rng):
        if player_roles[executed] != "Boomdandy":
            return False

        if (rng.randint(1, 3) == 1):
            return "Boom"
        else:
            return "Doom"
        
class Witch:
    def on_player_executed(self, executed, alive, player_roles, rng):
        if rng.randint(1,len(alive)+1) == 1:
            targets = getGoodtargets(alive, player_roles)
            if targets:
                target = rng.choice(targets)
                kill(alive, target, rng)

class Goblin:
    def on_player_executed(self, executed, alive, player_roles, rng):
        if player_roles[executed] != "Goblin":
            return False
        return "Doom"

class Saint:
    def on_player_executed(self, executed, alive, player_roles, rng):
        if player_roles[executed] != "Saint":
            return False
        return "Doom"

ROLE_HOOKS = {
    "PoppyGrower": PoppyGrower,
    "Assassin": Assassin,
    "Godfather": Godfather,
    "DA": DA,
    "Boomdandy": Boomdandy,
    "Goblin": Goblin,
    "Witch": Witch,
    "Demon": ScarletWoman,
    "Saint": Saint
}

ALIGNMENTS = {
    "Demon": 0,
    "Minion": 0,
    "ScarletWoman": 0,
    "Good": 1,
    "Outsider": 1,
    "PoppyGrower": 1,
    "Assassin": 0,
    "Godfather": 0,
    "DA": 0,
    "Boomdandy": 0,
    "Goblin": 0,
    "Saint": 1,
    "Klutz": 1,
    "Witch": 0
}

def getGoodtargets(alive, player_roles):
    global a_poppy
    global demon
    if a_poppy:
        return [p for p in alive if p != demon]
    else:
        return [p for p in alive if ALIGNMENTS[player_roles[p]] == 1]

def kill(alive, target, rng):
    global player_roles
    alive.remove(target)
    if player_roles[target] == "Klutz":
        possible_targets = [p for p in alive]
        if ALIGNMENTS[player_roles[rng.choice(possible_targets)]] == 0:
            for i in alive:
                if i != demon:
                    alive.remove(i)

def Game(roles, rng=None, role_hooks=None):
    """ Simulate a Blood on the Clocktower game with fully generic hooks.
        roles: list of strings, one per player
        role_hooks: dict mapping role name -> Role instance (can define any hooks)
        rng: random.Random instance or None
    """

    global a_poppy
    global demon

    rng = rng or random
    N = len(roles)

    player_roles = roles.copy()
    role_hooks = {r: ROLE_HOOKS[r]() for r in roles if r in ROLE_HOOKS}

    # Identify the demon player and its hook
    demon = player_roles.index("Demon")
    demon_hook = role_hooks.get("Demon", Role)

    players = set(range(N))
    alive = set(players)

    # Setup
    if "PoppyGrower" in player_roles:
        a_poppy = True
    else:
        a_poppy = False

    for hook_name, hook in role_hooks.items():
        if hasattr(hook, "setup"):
            hook.setup(alive, player_roles)

    num_days = 0
    num_nights = 0
    demon_executed_day = None

    def alive_counts():
        e = sum(1 for p in alive if ALIGNMENTS.get(player_roles[p], 0) == 0)
        g = sum(1 for p in alive if ALIGNMENTS.get(player_roles[p], 1) == 1)
        return e, g

    ae, ag = alive_counts()
    if ag == 0:
        return {"winner": "Evil", "num_days": 0, "num_nights": 0, "demon_executed_day": None}

    while True:

        ######### DAY #########
        num_days += 1
        target = rng.choice(list(alive))
        kill(alive, target, rng)

        # Execution hooks
        for role, hook in role_hooks.items():
            if hasattr(hook, "on_player_executed"):
                role_players = [p for p, r in enumerate(player_roles) if r == role]
                alive_role_players = [p for p in role_players if p in alive]

                if role in {"Boomdandy", "Goblin"}:
                    execution_saved = hook.on_player_executed(target, alive, player_roles, rng)
                else:
                    if not alive_role_players:
                        continue
                    execution_saved = hook.on_player_executed(target, alive, player_roles, rng)

                if execution_saved == "Boom":
                    return {"winner": "Good",
                            "num_days": num_days,
                            "num_nights": num_nights,
                            "demon_executed_day": demon_executed_day}

                if execution_saved == "Doom":
                    return {"winner": "Evil",
                            "num_days": num_days,
                            "num_nights": num_nights,
                            "demon_executed_day": demon_executed_day}

        # Demon executed?
        if demon not in alive:
            if demon_hook.on_demon_killed(alive, player_roles, demon, num_days):
                demon_executed_day = num_days
                return {"winner": "Good",
                        "num_days": num_days,
                        "num_nights": num_nights,
                        "demon_executed_day": demon_executed_day}

        ae, ag = alive_counts()
        if ag == 0:
            return {"winner": "Evil",
                    "num_days": num_days,
                    "num_nights": num_nights,
                    "demon_executed_day": None}

        ######### NIGHT #########
        for role, hook in role_hooks.items():
            if hasattr(hook, "on_night_action"):
                role_players = [p for p, r in enumerate(player_roles) if r == role]
                alive_role_players = [p for p in role_players if p in alive]
                if not alive_role_players:
                    continue

                result = hook.on_night_action(alive, player_roles, demon, rng)
                if result == "PoppyKill":
                    a_poppy = True

        # Default demon kill
        if demon in alive:
            targets = getGoodtargets(alive, player_roles)
            if targets:
                night_target = rng.choice(targets)
                kill(alive, night_target, rng)

        num_nights += 1

        ae, ag = alive_counts()
        if ag == 0:
            return {"winner": "Evil",
                    "num_days": num_days,
                    "num_nights": num_nights,
                    "demon_executed_day": None}

#rng = random.Random(1902)
#result = Game(roles=["Demon", "ScarletWoman", "Minion", "Outsider", "Outsider", "Good", "Good", "Good", "Good", "Good",  "Good",  "Good"], rng=rng)
#print(result)
