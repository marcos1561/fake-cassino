import numpy as np 
from math import log

from . import variance 
from ..roulette import settings
from ..roulette.colors import ColorMapper, Color

probs = settings.probs
luck_var_map = variance.variance_look_table(
    [settings.probs[ColorMapper.colors[i]] for i in range(3)])
bets_ids = variance.BetsId(len(ColorMapper.colors))

pr, pb, pw = probs[Color.red], probs[Color.black], probs[Color.white]
luck_value = {
    Color.black: (log(pb, 1/2), -pb/(1-pb)*log(pb, 1/2)),
    Color.red: (log(pr, 1/2), -pr/(1-pr)*log(pr, 1/2)),
    Color.white: (log(pw, 1/2), -pw/(1-pw)*log(pw, 1/2)),
}

luck_rows = {}
for c in ColorMapper.colors:
    l_row = []
    for c2 in ColorMapper.colors:
        id = 1
        if c is c2:
            id = 0
        l_row.append(luck_value[c2][int(c2 is not c)])
    luck_rows[c.value] = np.array(l_row)

def get_rolls(num_rounds):
    p_br = settings.probs[Color.red]

    rolls_rng = np.random.random(num_rounds)
    rolls = np.zeros(num_rounds, dtype=int)
    rolls[rolls_rng < p_br] = Color.black.value
    rolls[rolls_rng > 2*p_br] = Color.white.value
    return rolls

def get_std(bets: np.ndarray):
    ids = bets_ids.get_id(bets)
    
    var = 0
    for id in ids:
        if id == 1:
            continue

        var += luck_var_map[id]

    return var**.5

def calc_luck(rolls, strat):
    bets = strat(rolls)
    pr, pb, pw = probs[Color.red], probs[Color.black], probs[Color.white]

    luck_matrix = np.empty_like(bets, dtype=np.float64)
    for idx, roll in enumerate(rolls):
        luck_matrix[idx, :] = luck_rows[roll]

    luck = (luck_matrix * bets).sum()
    return luck

def get_luck(bet, roll):
    return luck_rows[roll].dot(bet)

def get_var(bet):
    id = bets_ids.get_id_single(bet)
    return luck_var_map[id]
