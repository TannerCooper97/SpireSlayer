from rest_framework import serializers
from .models import Deck, Card, DeckCard, UpgradedCard, Relic

class CardSynergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['id', 'name']

class RelicSynergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Relic
        fields = ['id', 'name']

class CardSerializer(serializers.ModelSerializer):
    synergies = CardSynergySerializer(many=True, read_only=True)
    relic_synergies = RelicSynergySerializer(many=True, read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='card-detail',
        lookup_field='id'
    )

    class Meta:
        model = Card
        fields = [
            'id',
            'card_color',
            'rarity',
            'name',
            'description',
            'energy',
            'damage',
            'block',
            'synergies',
            'relic_synergies',
            'url'
        ]

class UpgradedCardSerializer(serializers.ModelSerializer):
    original_card = serializers.HyperlinkedRelatedField(
        view_name='card-detail',  # Ensure this matches the router-generated URL name
        lookup_field='id',  # This should be pointing to the original card id
        queryset=Card.objects.all()  # Ensure this queryset is correct
    )
    
    class Meta:
        model = UpgradedCard
        fields = [
            'id',
            'upgraded_name',
            'upgraded_description',
            'upgraded_energy',
            'upgraded_damage',
            'upgraded_block',
            'original_card',
        ]

class DeckCardSerializer(serializers.ModelSerializer):
    card = CardSynergySerializer()

    class Meta:
        model = DeckCard
        fields = ['card', 'count']

class DeckSerializer(serializers.ModelSerializer):
    cards = DeckCardSerializer(source='deckcard_set', many=True)
    total_cards = serializers.SerializerMethodField()

    class Meta:
        model = Deck
        fields = [
            'id',
            'name',
            'description',
            'total_cards',
            'cards',
        ]

    def get_total_cards(self, obj):
        return obj.total_cards()

    def create(self, validated_data):
        cards_data = validated_data.pop('deckcard_set')
        deck = Deck.objects.create(**validated_data)
        for card_data in cards_data:
            DeckCard.objects.create(deck=deck, card=card_data['card'], count=card_data['count'])
        return deck

    def update(self, instance, validated_data):
        cards_data = validated_data.pop('deckcard_set')
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        # Update DeckCard relationships
        instance.deckcard_set.all().delete()
        for card_data in cards_data:
            DeckCard.objects.create(deck=instance, card=card_data['card'], count=card_data['count'])

        return instance

class RelicSerializer(serializers.ModelSerializer):
    synergistic_cards = CardSynergySerializer(many=True, read_only=True)

    class Meta:
        model = Relic
        fields = [
            'id',
            'name',
            'description',
            'synergistic_cards',
        ]