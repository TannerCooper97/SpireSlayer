from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Deck, Card, UpgradedCard, Relic
from .serializers import DeckSerializer, CardSerializer, UpgradedCardSerializer, RelicSerializer

class DeckViewSet(viewsets.ModelViewSet):
    queryset = Deck.objects.all()
    serializer_class = DeckSerializer

    @action(detail=True, methods=['post'])
    def add_card(self, request, pk=None):
        deck = self.get_object()
        card_ids = request.data.get('ids') # Accept a list of card IDs
        if not isinstance(card_ids, list):
            return Response({'status':'ids should be a list'}, status=400)
        try:
            cards = Card.objects.filter(id__in=card_ids)
            if len(cards) != len(card_ids):
                return Response({'status':'one or more cards not found'}, status=400)
            deck.cards.add(*cards)
            return Response({'status': 'card added'})
        except Card.DoesNotExist:
            return Response({'status': 'one or more cards not found'}, status=404)
    
    @action(detail=True, methods=['delete'])
    def remove_cards(self, request, pk=None):
        deck = self.get_object()
        card_ids = request.data.get('ids')  # Accept a list of card IDs
        if not isinstance(card_ids, list):
            return Response({'status': 'ids should be a list'}, status=400)
        try:
            cards = Card.objects.filter(id__in=card_ids)
            if len(cards) != len(card_ids):
                return Response({'status': 'one or more cards not found'}, status=404)
            deck.cards.remove(*cards)
            return Response({'status': 'cards removed'})
        except Card.DoesNotExist:
            return Response({'status': 'one or more cards not found'}, status=404)
        
class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
    lookup_field = 'id'

class UpgradedCardViewSet(viewsets.ModelViewSet):
    queryset = UpgradedCard.objects.all()
    serializer_class = UpgradedCardSerializer

class RelicViewSet(viewsets.ModelViewSet):
    queryset = Relic.objects.all()
    serializer_class = RelicSerializer