from django.db import models
from django.contrib.auth.models import User
from .roulette.colors import ColorMapper

class Beter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    money_spend = models.FloatField(default=0)
    money_won = models.FloatField(default=0)
    gain = models.FloatField(default=0)
    has_changed = models.BooleanField(default=False)
    
    luck = models.FloatField(default=0)
    luck_var = models.FloatField(default=0)
    gain_expected = models.FloatField(default=0)
    gain_var = models.FloatField(default=0)
    num_bets_processed = models.IntegerField(default=0)

    def __str__(self):
        name = self.user.username
        return f"{name}: {self.balance}"

class RoletinhaHistory(models.Model):
    color = models.IntegerField()
    date = models.DateTimeField()

    def __str__(self):
        color = ColorMapper.to_id(self.color, inverse=True)
        color = ColorMapper.to_str(color)
        return color

class BetHistory(models.Model):
    round = models.ForeignKey(RoletinhaHistory, on_delete=models.CASCADE)
    beter = models.ForeignKey(Beter, on_delete=models.CASCADE)
    amount = models.FloatField()
    color = models.IntegerField()
    won = models.BooleanField()
    date = models.DateTimeField()

    def __str__(self):
        name = self.beter.user.username
        color = ColorMapper.to_id(self.color, inverse=True)
        color = ColorMapper.to_str(color)
        return f"{name}: {self.amount}, {color}, {self.won}"

class Cassino(models.Model):
    balance = models.FloatField(default=0)

