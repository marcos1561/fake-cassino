from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import Beter

@receiver(post_save, sender=User)
def create_better(sender, instance, created, **kwargs):
    if created:
        Beter.objects.create(user=instance, balance=10000)