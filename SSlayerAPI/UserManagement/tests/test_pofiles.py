from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile

class ProfileModelTest(TestCase):

    def setUp(self):
        # Create a user for testing
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_profile(self):
        # Test creating a profile for the user
        profile = Profile.objects.create(user=self.user, first_name='Test', last_name='User', bio='This is a test bio.')
        self.assertEqual(profile.user.username, 'testuser')
        self.assertEqual(profile.first_name, 'Test')
        self.assertEqual(profile.last_name, 'User')
        self.assertEqual(profile.bio, 'This is a test bio.')

    def test_duplicate_profile_creation(self):
        # Create the first profile
        Profile.objects.create(user=self.user, first_name='Test', last_name='User', bio='This is a test bio.')

        # Attempt to create a duplicate profile
        with self.assertRaises(ValidationError):
            duplicate_profile = Profile(user=self.user, first_name='Duplicate', last_name='User', bio='This is a duplicate bio.')
            duplicate_profile.save()