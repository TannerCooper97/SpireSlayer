from rest_framework import serializers
from .models import Profile  # Correct the import path

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'