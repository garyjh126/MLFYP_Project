from django.db import models

# Create your models here.

class Game(models.Model):
    total_pot = models.CharField(max_length=20)
    guest_cards = models.ForeignKey('CardHolding', related_name='guest_cards', on_delete=models.CASCADE)
    learner_cards = models.ForeignKey('CardHolding', related_name='learner_cards', on_delete=models.CASCADE)
    community_cards = models.ForeignKey('CommunityCards', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Total Pot: {}\nGuest Cards: {}\nLearner Cards: {}\nCommunity Cards: {}\n".format(self.total_pot, self.guest_cards, self.learner_cards, self.community_cards)

class CommunityCards(models.Model):
    flop_0 = models.ForeignKey('Card', default="", related_name='flop_0', on_delete=models.CASCADE)
    flop_1 = models.ForeignKey('Card', default="", related_name='flop_1', on_delete=models.CASCADE)
    flop_2 = models.ForeignKey('Card', default="", related_name='flop_2', on_delete=models.CASCADE)
    turn = models.ForeignKey('Card', default="", related_name='turn', on_delete=models.CASCADE)
    river = models.ForeignKey('Card', default="", related_name='river', on_delete=models.CASCADE)

    def __str__(self):
        return "{}{}{}{}{}".format(self.flop_0, self.flop_1, self.flop_2, self.turn, self.river)

class CardHolding(models.Model):
    first = models.ForeignKey('Card', default="", related_name='first', on_delete=models.CASCADE)
    second = models.ForeignKey('Card', default="", related_name='second', on_delete=models.CASCADE)

    def __str__(self):
        return "{},{}".format(self.first, self.second)


class Card(models.Model):
    # It includes 13 ranks in each of the four French suits: clubs (♣), diamonds (♦), hearts (♥) and spades (♠)
    rank = models.CharField(max_length=2, default="", null=True)
    suit = models.CharField(max_length=2, default="", null=True)

    def __str__(self):
        return "{}{}".format(self.rank, self.suit)
