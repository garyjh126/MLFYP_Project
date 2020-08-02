from rest_framework import serializers
from .models import *

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('total_pot', 'guest_cards', 'learner_cards', 'community_cards')
