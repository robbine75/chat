from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from .models import Profile


class ChatModelTest(TestCase):
    def setUp(self):
        """ Setup some initial users. """
        self.user_bob = User.objects.create_user(username='test_model_user1',
                                                 password='12345')
        self.user_bob.save()

        self.user_steve = User.objects.create_user(username='test_model_user2',
                                                   password='12345')
        self.user_steve.save()

    def test_models_profile(self):
        # Note: We don't have separate Redis for tests.
        result = Profile.get_online_users()
        self.assertNotIn('test_model_user1', result)
        self.assertNotIn('test_model_user2', result)

        # Go to any page to trigger active_user_middleware middleware.
        self.client.login(username='test_model_user1', password='12345')
        self.client.get(reverse('core:user_list'))

        # Check if test_model_user1 are online.
        profile, _ = Profile.objects.get_or_create(user=self.user_bob)
        self.assertEqual(str(profile), 'test_model_user1')

        # Check a list of online users.
        result = Profile.get_online_users()
        self.assertIn('test_model_user1', result)

        # Go to any page to trigger active_user_middleware middleware.
        self.client.login(username='test_model_user2', password='12345')
        self.client.get(reverse('core:user_list'))

        # Check if user are online.
        profile, _ = Profile.objects.get_or_create(user=self.user_steve)
        self.assertEqual(str(profile), 'test_model_user2')

        # Check a list of online users.
        result = Profile.get_online_users()
        self.assertGreaterEqual(len(result), 2)
        self.assertIn('test_model_user1', result)
        self.assertIn('test_model_user2', result)

        # Clean up the cache.
        cache.delete('seen_{}'.format('test_model_user1'))
        cache.delete('seen_{}'.format('test_model_user2'))
