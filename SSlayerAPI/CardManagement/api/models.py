from django.db import models, transaction
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver

class Card(models.Model):
    # Create Card Choices for each character or type of card
    COLOR_CHOICES = [
        ('Green', 'Green'),
        ('Red', 'Red'),
        ('Blue', 'Blue'),
        ('Purple', 'Purple'),
        ('Grey', 'Grey'),
        ('Black', 'Black'),
        ('White', 'White')
    ]

    CARD_RARITY = [
        ('Starter', 'Starter'),
        ('Common', 'Common'),
        ('Uncommon', 'Uncommon'),
        ('Rare', 'Rare'),
    ]

    card_color = models.CharField(max_length=6, choices=COLOR_CHOICES, default='White')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    energy = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)])
    damage = models.IntegerField(default=0)
    block = models.IntegerField(default=0)
    synergies = models.ManyToManyField('self', blank=True, symmetrical=False, related_name='synergistic_with') #Self reference
    relic_synergies = models.ManyToManyField('Relic', blank=True, related_name='cards_with_synergies')
    rarity = models.CharField(max_length=8, choices=CARD_RARITY, default='Common')

    def __str__(self):
        return self.name
    #Overrite save method to set the ID, only if the instance is new (if not self.pk). This ensures existing instances retain their IDs.
    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the ID if it's a new instance
            self.pk = self.generate_next_id()
        super().save(*args, **kwargs)

    #generate_next_id calculates the next ID based on the card_color. It uses a prefix for each color and finds the last card of the same color to determine the next ID.
    def generate_next_id(self):
        #color_prefix maps each card_color to a specific prefix. The next ID is calculated by adding 1 to the last card's ID or starting from the prefix + 1 if no cards exist for that color
        color_prefix = {
            'Green': 1000,
            'Red': 2000,
            'Blue': 3000,
            'Purple': 4000,
            'Grey': 5000,
            'Black': 6000,
            'White': 7000
        }
        prefix = color_prefix.get(self.card_color, 5000)
        #generate_next_id method is wrapped in a transaction.atomic() block to ensure that the ID generation process is atomic.
        with transaction.atomic():
            #select_for_update method is used to lock the rows until the transaction is complete. This prevents other transactions from reading or writing to the locked rows, ensuring that no two transactions can generate the same ID simultaneously.
            last_card = Card.objects.select_for_update().filter(card_color=self.card_color).order_by('-id').first()
            #The next ID is calculated by adding 1 to the last card's ID or starting from the prefix + 1 if no cards exist for that color.
            if last_card:
                next_id = last_card.id + 1
            else:
                next_id = prefix + 1
            return next_id

class Deck(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    cards = models.ManyToManyField(Card, related_name='decks')

    def __str__(self):
        return self.name
    
    def total_cards(self):
        #.aggregate(total=models.Sum('count')): The aggregate function is used to perform aggregation operations on a queryset. models.Sum('count') calculates the sum of the count field for all DeckCard instances related to the current Deck instance. The result of the aggregation is a dictionary with the key 'total' and the value being the sum of the count field.
        return self.deckcard_set.aggregate(total=models.Sum('count'))['total'] or 0

#Deck Card model represents the many-to-many relationship between Deck and Card with an additional count field to track the number of each card in the deck.
class DeckCard(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    count = models.PositiveIntegerField(default=1)

    class Meta:
        #tuple of field names that must be unique together. It is used to enforce a multi-column unique constraint at the database level. This specifies that the combination of deck and card must be unique.
        unique_together = ('deck', 'card')

    def __str__(self):
        return f"{self.deck.name} - {self.card.name} (x{self.count})"

class UpgradedCard(models.Model):
    # Grabs the original cards data and creates/updates a 'upgraded card' to show card after you upgrade it. Created its own model/table so its easier to maintain the Card Model/Table within the database.
    original_card = models.OneToOneField(Card, related_name='upgraded_version', on_delete=models.CASCADE)
    upgraded_name = models.CharField(max_length=100, blank=True)
    upgraded_description = models.TextField(blank=True)
    upgraded_energy = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(10)], null=True, blank=True)
    upgraded_damage = models.IntegerField(null=True, blank=True)
    upgraded_block = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Upgraded {self.original_card.name}"
    
     #Checks if ther were any changes made to the name, description, energy, and if not keeps the same values.
@receiver(post_save, sender=UpgradedCard)
def set_default_values(sender, instance, created, **kwargs):
    if created:
        if not instance.upgraded_name:
            instance.upgraded_name = instance.original_card.name
        if not instance.upgraded_description:
            instance.upgraded_description = instance.original_card.description
        if instance.upgraded_energy is None:
            instance.upgraded_energy = instance.original_card.energy
        if instance.upgraded_damage is None:
            instance.upgraded_damage = instance.original_card.damage
        if instance.upgraded_block is None:
            instance.upgraded_block = instance.original_card.block    
        # Use update to avoid recursion
        UpgradedCard.objects.filter(pk=instance.pk).update(
            upgraded_name=instance.upgraded_name,
            upgraded_description=instance.upgraded_description,
            upgraded_energy=instance.upgraded_energy,
            upgraded_damage=instance.upgraded_damage,
            upgraded_block=instance.upgraded_block
        )

class Relic(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    synergistic_cards = models.ManyToManyField(Card, blank=True, related_name='relics_with_synergies')

    def __str__(self):
        return self.name

@receiver(m2m_changed, sender=Card.synergies.through)
def update_card_synergies(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            related_card = Card.objects.get(pk=pk)
            if not related_card.synergistic_with.filter(pk=instance.pk).exists():
                related_card.synergistic_with.add(instance)

@receiver(m2m_changed, sender=Relic.synergistic_cards.through)
def update_relic_synergies(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == 'post_add':
        for pk in pk_set:
            related_card = Card.objects.get(pk=pk)
            if not related_card.relic_synergies.filter(pk=instance.pk).exists():
                related_card.relic_synergies.add(instance)