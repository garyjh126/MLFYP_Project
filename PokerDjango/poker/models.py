from django.db import models
from treys import *
from djmoney.models.fields import MoneyField
from djmoney.money import Money

class Game(models.Model):

    total_pot = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')
    players = models.ManyToManyField('Player')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Total Pot: {}\tGuest Cards: {}\tLearner Cards: {}\tCommunity Cards: {}\tPlayers: {}".format(self.total_pot, __str__(self.guest_cards), __str__(self.learner_cards), __str__(self.community_cards), __str__(self.players))

    @classmethod
    def create(cls, total_pot, players):
        
        game = cls(total_pot=Money(total_pot, 'USD'), players=players)
        # do something with the book
        return game

    class Meta: 
        ordering = ["created_at"]

class Player(models.Model):
    name = models.CharField(max_length=100, default="Player")
    stack = MoneyField(max_digits=14, decimal_places=2, default_currency='USD')

    @classmethod
    def create(cls, name, stack):
        
        game = cls(name=name, stack=Money(stack, 'USD'))
        # do something with the book
        return game

    def __str__(self):
        return "Name: {}\tStack: {}".format(self.name, self.stack)
    

class Card(models.Model):
    card_str = models.CharField(max_length=2, null=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url

    class Meta:
        abstract = True

class Card_Player(Card):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    
class Card_Community(Card):
    game = models.ForeignKey('Game', on_delete=models.CASCADE)