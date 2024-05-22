import numpy as np
import itertools

def get_primes(n):
    from math import ceil

    primes = [2]
    i = 3
    while len(primes) < n:
        num_divs = 0
        for j in range(2, ceil(i**.5)+1):
            if i % j == 0:
                num_divs += 1
                break
        
        if num_divs == 0:
            primes.append(i)
        
        i+=1
    
    return primes

def luck_variance(probs_win: np.ndarray):
    t1 = probs_win/(1-probs_win) * (np.log(probs_win)/np.log(1/2))
    l = t1.sum()
    t2 = np.square(t1)/probs_win
    return t2.sum() - l**2

class BetsId:
    def __init__(self, num_options):
        self.primes = get_primes(num_options)
        self.primes_row = np.array(self.primes)

    def get_id(self, bets: np.ndarray):
        primes_arr = np.empty_like(bets, dtype=float)
        for idx, p in enumerate(self.primes):
            primes_arr[:, idx] = p

        ids = (primes_arr**bets).prod(axis=1)
        return ids.astype(int)
    
    def get_id_single(self, bet):
        return int((self.primes_row**bet).prod())

def variance_look_table(probs):
    if type(probs) != np.ndarray:
        probs = np.array(probs)

    n = probs.size
    possible_bets = []
    for i in range(n):
        row = np.zeros(n)
        row[:i+1] = 1
        possible_bets.extend(list(set(itertools.permutations(row, row.size))))
    possible_bets = np.array(possible_bets, dtype=bool)

    primes_mask = np.empty(possible_bets.shape)
    primes = np.array(get_primes(len(probs)))
    for i in range(n):
        primes_mask[:, i] = primes[i]

    bets_ids = BetsId(n).get_id(possible_bets)

    variance_map = {}
    for b_id, p_mask in zip(bets_ids, possible_bets):
        variance_map[int(b_id)] = luck_variance(probs[p_mask])

    return variance_map

if __name__ == "__main__":
    p_rb = 0.47
    p_w = 1 - 2*p_rb

    probs = [
        [p_rb],
        [p_rb],
        [p_w],
        [p_rb, p_rb],
        [p_rb, p_w],
        [p_rb, p_w],
        [p_rb, p_rb, p_w],
    ]
    for p in probs:
        var = luck_variance(np.array(p))
        # print(round(var, 5))

    # print(variance_look_table())
