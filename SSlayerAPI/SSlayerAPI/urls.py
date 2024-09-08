"""
URL configuration for SSlayerAPI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from UserManagement.api.views import ProfileViewSet
from CardManagement.api.views import DeckViewSet, CardViewSet, UpgradedCardViewSet, RelicViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'decks', DeckViewSet)
router.register(r'cards', CardViewSet, basename='card')
router.register(r'relics', RelicViewSet)
router.register(r'upgraded_cards', UpgradedCardViewSet)

# The API URLs determined automatically by the router.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/user-management/', include('UserManagement.api.urls')),
    path('api/card-management/', include('CardManagement.api.urls')),
    path('', include(router.urls)),  # Include the router URLs at the root
]