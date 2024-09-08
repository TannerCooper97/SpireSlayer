from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# User Profile Model
class Profile(models.Model):
    #Users cannot have more then one profile.
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

    # Not needed, here for legibility
    @property
    def is_superuser(self):
        return self.user.is_superuser

    # Not needed, here for legibility
    @property
    def is_staff(self):
        return self.user.is_staff
    
    def save(self, *args, **kwargs):
        if Profile.objects.filter(user=self.user).exists() and not self.pk:
            raise ValidationError(f'Profile for user {self.user.username} already exists.')
        super().save(*args, **kwargs)