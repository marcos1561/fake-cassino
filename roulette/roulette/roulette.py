import random, time, threading
from enum import Flag, Enum, auto

from django.utils import timezone
from roulette.models import Cassino, Beter, BetHistory, RoletinhaHistory
from .colors import Color, ColorMapper
from . import settings  


is_making_migrations = False

class LowMoneyError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__("Dinheiro insuficiente para fazer a aposta.")

class State(Flag):
    waiting = auto()
    rolling = auto()
    finished = auto()

class Bet():
    def __init__(self, amount: float, color: Color, beter_id) -> None:
        self.beter_id = beter_id
        self.amount = amount
        self.color = color

class BeterInfo():
    def __init__(self, beter: Beter, money_spend) -> None:
        self.beter = beter
        self.gain = 0
        self.money_spend = money_spend
        self.money_won = 0

class History():
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        
        h = list(RoletinhaHistory.objects.order_by("-date")[:capacity])
        h.reverse()

        self.items = [-1 for _ in range(capacity)]
        for id, roll in enumerate(h):
            self.items[id] = roll.color

    def add(self, item: int):
        self.items[1:] = self.items[:-1]
        self.items[0] = item

    def get(self, num=None):
        if num is None:
            return self.items
        else:
            return self.items[:num]


class Roletinha:
    probs = settings.probs

    multiplier = settings.multiplier

    def __init__(self, Cassino: type[Cassino], is_making_migration=False) -> None:
        print("Roletinha iniciando")

        if is_making_migration:
            return

        total_p = 0
        for color in ColorMapper.colors:
            total_p += self.probs[color]
        if total_p != 1:
            raise Exception("Probabilidades não somam em 1.")

        self.Cassino = Cassino
        self.cassino_gain = 0 
        self.history = History(1000)
        self.state = State.waiting
        self.color_rolled = None
        self.has_rolled = False

        self.num_bets = 0
        
        self.bets: list[Bet] = []
        self.beters_info: dict[int, BeterInfo] = {}

        self.bets_amount = {
            Color.red: 0,
            Color.black: 0,
            Color.white: 0,
        }

    @property
    def balance(self):
        return self.Cassino.objects.all()[0].balance

    def register_bet(self, amount: float, color: Color | str, beter: Beter):
        if self.state is not State.waiting:
            return
        
        amount = float(amount)

        if amount < 0:
            raise Exception("Valor da aposta negativo.")

        beter_info = self.beters_info.get(beter.id, None)
        current_amount = 0
        if beter_info is not None:
            current_amount = beter_info.money_spend

        if amount > (beter.balance - current_amount):
            raise LowMoneyError()

        if type(color) == str:
            color = ColorMapper.to_str(color, inverse=True)

        self.bets.append(Bet(amount, color, beter.id))
        self.num_bets += 1 
        
        if beter_info is not None:
            beter_info.money_spend += amount 
        else:
            self.beters_info[beter.id] = BeterInfo(beter, amount)

        self.bets_amount[color] += amount

    def roll(self):
        rng = random.random()
        
        if rng < self.probs[Color.red]:
            color_rolled = Color.red
        elif rng < self.probs[Color.red] + self.probs[Color.black]: 
            color_rolled = Color.black
        else:
            color_rolled = Color.white

        return color_rolled

    def process_bets(self):
        color_id = ColorMapper.to_id(self.color_rolled)
        self.history.add(color_id)
        roulette_round = RoletinhaHistory.objects.create(
            color = color_id,
            date = timezone.now(),
        )

        for bet in self.bets:
            reward = 0
            cassino_lost = bet.color == self.color_rolled
            if cassino_lost:
                reward = bet.amount * self.multiplier[self.color_rolled]
            
            self.cassino_gain += bet.amount - reward
            
            beter_info = self.beters_info[bet.beter_id]
            beter_info.money_won += reward
            beter_info.gain += -bet.amount + reward

            BetHistory.objects.create(
                round = roulette_round,
                beter = beter_info.beter,
                amount = bet.amount,
                color = ColorMapper.to_id(bet.color),
                won = cassino_lost,
                date = timezone.now(),
            )

    def update_wallets(self):
        for beter_info in self.beters_info.values():
            beter = beter_info.beter

            beter.balance += beter_info.gain
            beter.gain += beter_info.gain
            beter.money_won += beter_info.money_won
            beter.money_spend += beter_info.money_spend
            beter.has_changed = True
            beter.save()

        cassino_db = self.Cassino.objects.all()[0]
        cassino_db.balance += self.cassino_gain
        cassino_db.save()

    def reset(self):
        self.num_bets = 0
        self.bets = []
        self.beters_info = {}
        self.cassino_gain = 0
        self.has_rolled = False
        for key in self.bets_amount.keys():
            self.bets_amount[key] = 0

    def run(self):
        while True:
            self.state = State.waiting
            self.status_changed = True
            self.color_rolled = None
            time.sleep(15)

            
            self.state = State.rolling
            self.status_changed = True
            self.color_rolled = self.roll()
            self.has_rolled = True
            time.sleep(1)


            self.state = State.finished
            self.status_changed = True
            self.new_roll = True
            self.process_bets()
            self.update_wallets()
            time.sleep(4)
            self.reset()

roletinha = Roletinha(Cassino, is_making_migrations)
if not is_making_migrations:
    threading.Thread(target=roletinha.run, daemon=True).start()