from django.db import models
from treys import *
from djmoney.models.fields import MoneyField
from djmoney.money import Money

class Game(models.Model):

    total_pot = models.DecimalField(max_digits=20, decimal_places=2)
    players = models.ManyToManyField('Player', related_name='games', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, *args):
        
        game = cls(total_pot=args[0])

        return game

    class Meta: 
        ordering = ["created_at"]

    def __str__(self):
        return str(self.id)

class Player(models.Model):
    name = models.CharField(max_length=100, default="Player")
    stack = models.DecimalField(max_digits=20, decimal_places=2)

    @classmethod
    def create(cls, name, stack):
        return cls(name=name, stack=stack)

    def __str__(self):
        return self.name

class Card(models.Model):
    card_str = models.CharField(max_length=2, null=True)

    class Meta:
        abstract = True

class Card_Player(Card):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)

class Card_Community(Card):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
