from rest_framework import serializers
from .models import *

class GameSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(read_only=True)
    total_pot = serializers.CharField(max_length=20)
    guest_cards = serializers.CharField()
    learner_cards = serializers.CharField()
    community_cards = serializers.CharField()

    # Consider using image area for card representation {'base_template': 'textarea.html'}
    def create(self, validated_data):
        """
        Create and return a new `Game` instance, given the validated data.
        """
        return Game.objects.create(**validated_data)

    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing `Snippet` instance, given the validated data.
    #     """
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.code = validated_data.get('code', instance.code)
    #     instance.linenos = validated_data.get('linenos', instance.linenos)
    #     instance.language = validated_data.get('language', instance.language)
    #     instance.style = validated_data.get('style', instance.style)
    #     instance.save()
    #     return instance

