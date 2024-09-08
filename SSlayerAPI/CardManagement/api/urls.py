from rest_framework.routers import DefaultRouter
from .views import DeckViewSet, CardViewSet, RelicViewSet, UpgradedCardViewSet

router = DefaultRouter()
router.register(r'decks', DeckViewSet)
router.register(r'cards', CardViewSet, basename='card')
router.register(r'relics', RelicViewSet)
router.register(r'upgraded_cards', UpgradedCardViewSet)

urlpatterns = router.urls