from rest_framework.serializers import ModelSerializer

from .models import (
    Game,
    Player,
    Card,
    Card_Player,
    Card_Community
)

class PlayerSerializer(ModelSerializer):

    class Meta:
        model = Player  
        fields = ['id', 'name', 'stack', 'games']
        extra_kwargs = {'games': {'required': False}}

class GameSerializer(ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ['id', 'total_pot', 'players', 'created_at']
        extra_kwargs = {'players': {'required': False}}

class CardSerializer(ModelSerializer):
    class Meta:
        model = Card
        abstract = True
    
class Card_PlayerSerializer(CardSerializer):
    class Meta:
        model = Card_Player
        fields = ['id', 'card_str', 'player']
    
class Card_CommunitySerializer(CardSerializer):
    class Meta:
        model = Card_Community
        fields = ['id', 'card_str', 'game']
    