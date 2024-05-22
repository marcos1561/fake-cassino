import locale
import numpy as np
from scipy import stats

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

from django.shortcuts import render

from .models import Beter, BetHistory
from .roulette import settings 
from .roulette.colors import ColorMapper
from .luck import utils as luck_utils

def gain_mean_variance(probs, values, ks):
    l = values.sum()
    
    mean = (probs*values*ks).sum() - l
    variance = (probs * (values * ks)**2).sum() - (mean+l)**2

    return mean, variance

class CassinoInfo:
    def __init__(self):
        self.user_info = []
        self.cassino_info = {
            "prob_gain": -1
        }
        
        self.probs = np.array([settings.probs[c] for c in ColorMapper.colors])
        self.ks = np.array([settings.multiplier[c] for c in ColorMapper.colors])

        # Informações das apostas feitas em uma rodada
        self.bet_amounts = np.zeros(3, dtype=np.float64)
        self.bet_colors = np.full(3, False)
        self.roll = -1
        self.current_round_id = -1 
        self.num_bets_in_round = -1

        self.is_updating = False

        self.update()

    def reset_saved_user_info(self):
        for beter in Beter.objects.all():
            beter.luck = 0
            beter.luck_var = 0
            beter.gain_expected = 0
            beter.gain_var = 0
            beter.num_bets_processed = 0
            beter.save()
              
    def update_user_quantities(self, bet_amounts, bet_colors, roll):
        self.luck += luck_utils.get_luck(bet_colors, roll)
        self.luck_var += luck_utils.get_var(bet_colors)
        
        gain_mean_i, gain_var_i = gain_mean_variance(self.probs, bet_amounts, self.ks)
        self.gain_mean += gain_mean_i
        self.gain_var += gain_var_i

    def reset_bet_info(self, bet):
        self.roll = bet.round.color
        self.bet_colors[:] = False
        self.bet_amounts[:] = 0
        self.current_round_id = bet.round.id
        self.num_bets_in_round = 0

    def process_bets(self, history):
        self.reset_bet_info(history[0])

        num_bets_processed = 0
        bet: BetHistory
        for bet in history:
            if bet.round.id != self.current_round_id:
                num_bets_processed += self.num_bets_in_round 
                self.update_user_quantities(self.bet_amounts, self.bet_colors, self.roll)
                self.reset_bet_info(bet)

            self.bet_colors[bet.color] = True
            self.bet_amounts[bet.color] += bet.amount
            self.num_bets_in_round += 1

        return num_bets_processed

    def update(self):
        if self.is_updating:
            return
        self.is_updating = True

        print("="*10)
        print("ATUALIZANDO")
        print("="*10)

        total_gain_mean = 0
        total_gain_var = 0
        self.user_info = []

        for beter in Beter.objects.all():
            num_bets_skip = beter.num_bets_processed
            history = beter.bethistory_set.order_by("date")[num_bets_skip:]
            num_bets = len(history)

            self.luck = beter.luck
            self.luck_var = beter.luck_var
            self.gain_mean = beter.gain_expected
            self.gain_var = beter.gain_var
            
            if num_bets > 0:
                num_bets_processed = self.process_bets(history)

                if num_bets_processed > 0:
                    beter.luck = self.luck
                    beter.luck_var = self.luck_var
                    beter.gain_expected = self.gain_mean
                    beter.gain_var = self.gain_var
                    beter.num_bets_processed = num_bets_skip + num_bets_processed
                    beter.save()

                self.update_user_quantities(self.bet_amounts, self.bet_colors, self.roll)
            
            total_gain_mean += self.gain_mean
            total_gain_var += self.gain_var

            gain_std = self.gain_var**.5

            min_gain = locale.currency(self.gain_mean - 2*gain_std, grouping=True)
            max_gain = locale.currency(self.gain_mean + 2*gain_std, grouping=True)
            gain_interval = f"[{min_gain}; {max_gain}]" 
            
            lost_prob = "0"
            if gain_std > 0:
                lost_prob = stats.norm.cdf(0, loc=self.gain_mean, scale=gain_std) * 100
                lost_prob = str(round(lost_prob, 2)).replace(".", ",")

            luck_value = "N/A"
            if self.luck_var > 0:
                luck_value = self.luck / self.luck_var**.5
                luck_value = str(round(luck_value, 4)).replace(".", ",")

            info = {"luck": 0, "gain_exp": 0, "gain": 0}
            info["luck"] = luck_value
            info["gain_exp"] = locale.currency(self.gain_mean, grouping=True)
            info["gain_interval"] = gain_interval
            info["lost_prob"] = lost_prob
            info["gain"] = locale.currency(beter.gain, grouping=True)

            self.user_info.append((beter.user.username, info))

        total_gain_std = total_gain_var**.5
        cassino_p_gain = stats.norm.cdf(0, loc=total_gain_mean, scale=total_gain_std)*100
        self.cassino_info["prob_gain"] = cassino_p_gain
        
        self.is_updating = False

cassino_info = CassinoInfo()

def user(request):
    if not request.user.is_authenticated:
        return render(request, "roulette/user.html", {"is_authenticated": False})

    cassino_info.update()
    return render(request, "roulette/user.html", {"content": cassino_info.user_info, "is_authenticated": True})
