import pickle
from .models import Beter

def get_users_bets():
    bets_data = {}
    for b in Beter.objects.all():
        beter_data = []
        for bet in b.bethistory_set.order_by("date"):
            beter_data.append({
                "round_id": bet.round.id,
                "roll_color": bet.round.color,
                "bet_color": bet.color,
                "bet_amount": bet.amount,
            })
        bets_data[b.user.username] = beter_data

    with open("bets_data.pickle", "wb") as f:
        pickle.dump(bets_data, f) 