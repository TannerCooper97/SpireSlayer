from django.contrib import admin
from CardManagement.api.models import Deck, Card, Relic, UpgradedCard, DeckCard

# DeckCardInline: Allows you to manage DeckCard instances directly within the Deck admin interface. '(admin.TabularInline):' Displays related objects in a tabular format.
class DeckCardInline(admin.TabularInline):
    model = DeckCard  # Specifies the model to be used in this inline
    extra = 1  # Number of extra empty forms to display
    verbose_name = "Card in Deck"  # Custom header text for the inline section
    verbose_name_plural = "Cards in Deck"  # Custom header text for the inline section

#DeckAdmin: Customizes the admin interface for the Deck model, including the inline DeckCard instances and excluding the redundant cards field.
class DeckAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'total_cards_display')  # Fields to display in the list view
    inlines = [DeckCardInline]  # Include the DeckCardInline in the Deck admin interface
    exclude = ('cards',)  # Exclude the 'cards' field to remove redundant info

    def total_cards_display(self, obj):
        return obj.total_cards()  # Method to display total cards
    total_cards_display.short_description = 'Total Cards'  # Custom column header

admin.site.register(Deck, DeckAdmin)  # Register Deck model with the custom DeckAdmin
admin.site.register(Card)  # Register Card model
admin.site.register(Relic)  # Register Relic model
admin.site.register(UpgradedCard)  # Register UpgradedCard model