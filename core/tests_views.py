from unittest import mock

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Thread


class ChatViewTest(TestCase):
    def setUp(self):
        # No need to set cache seen for tests users for testing views.
        view_patcher_cache = mock.patch('core.middleware.cache')
        self.mock_cache = view_patcher_cache.start()
        self.addCleanup(view_patcher_cache.stop)
        # Create usual user.
        test_user = User.objects.create_user(username='testuser',
                                             password='12345')
        test_user.save()
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='12345')
        test_user2.save()
        test_admin = User.objects.create_superuser(
            username='testadmin',
            email='myemail@test.com',
            password='12345'
        )
        test_admin.save()

    # Pages available for anonymous.
    def test_views_about(self):
        resp = self.client.get(reverse('core:about_page'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'about.html')

    def test_views_login(self):
        resp = self.client.get(reverse('core:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'login.html')

        # Try to login again (fail).
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:login'))
        self.assertRedirects(resp, reverse(settings.LOGIN_REDIRECT_URL))

    def test_views_signup(self):
        resp = self.client.get(reverse('core:signup'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'signup.html')

        # Try to login again (fail).
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:signup'))
        self.assertRedirects(resp, reverse(settings.LOGIN_REDIRECT_URL))

    def test_views_logout(self):
        resp = self.client.get(reverse('core:logout'))
        self.assertRedirects(resp, '/login?next=/logout')
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:logout'))
        self.assertRedirects(resp, reverse('core:login'))

    # Pages available only for registered users.
    def test_views_user_list(self):
        resp = self.client.get(reverse('core:user_list'))
        self.assertRedirects(resp, '/login?next=/')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'user_list.html')

    def test_views_chatbot(self):
        resp = self.client.get('/chat/chatbot')
        self.assertRedirects(resp, '/login?next=/chat/chatbot')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get('/chat/chatbot')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'thread.html')

    def test_views_user(self):
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertRedirects(resp, '/login?next=/user/testuser')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)

        self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)

    def test_views_update_profile(self):
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'first_name': 'test1'}
        )
        self.assertRedirects(resp, '/login?next=/user/testuser')
        self.client.login(username='testuser', password='12345')
        # Need to create profile for the users.
        resp = self.client.get(reverse('core:user',
                                       kwargs={'username': 'testuser'}))
        self.assertEqual(resp.status_code, 200)

        # Change first name.
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'name': 'first_name', 'value': 'test name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'test name')

        # Change last name.
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'name': 'last_name', 'value': 'test last name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.last_name, 'test last name')

        # Change email.
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'name': 'email', 'value': 'myemail2@test.com'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'myemail2@test.com')

        # Change not existing field (fail).
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'name': 'dummy_field', 'value': 'dummy_value'}
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            str(resp.content, encoding='utf8'),
            '"You can\'t change this field"'
        )

        # Admin can update profile for any user.
        self.client.login(username='testadmin', password='12345')
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'name': 'first_name', 'value': 'test name'}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertJSONEqual(
            str(resp.content, encoding='utf8'),
            {'success': True}
        )
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'test name')

        # User can update only his own profile.
        self.client.login(username='testuser2', password='12345')
        resp = self.client.post(
            reverse('core:user', kwargs={'username': 'testuser'}),
            {'name': 'first_name', 'value': 'test name fail'}
        )
        self.assertEqual(resp.status_code, 403)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.first_name, 'test name')

    def test_views_chat(self):
        resp = self.client.get(reverse('core:chat',
                                       kwargs={'username': 'testuser2'}))
        self.assertRedirects(resp, '/login?next=/chat/testuser2')

        # Go to chat page.
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:chat',
                                       kwargs={'username': 'testuser2'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'thread.html')

        # Check the database.
        chat = Thread.objects\
            .filter(users__username='testuser')\
            .filter(users__username='testuser2')
        self.assertEqual(len(chat), 1)
        self.assertEqual(str(chat[0]), 'testuser, testuser2')

        # Try to open the thread by id (our test thread have id 1).
        resp = self.client.get(reverse('core:thread',
                                       kwargs={'thread_id': chat[0].pk}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'thread.html')

        # Tread with id 404 doesn't exists.
        resp = self.client.get(reverse('core:thread',
                                       kwargs={'thread_id': '404'}))
        self.assertEqual(resp.status_code, 404)

    def test_views_call(self):
        resp = self.client.get(reverse('core:call',
                                       kwargs={'username': 'testuser2'}))
        self.assertRedirects(resp, '/login?next=/call/testuser2')

        # Go to chat page.
        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:call',
                                       kwargs={'username': 'testuser2'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'call.html')

    def test_users_map_page(self):
        resp = self.client.get(reverse('core:users_map'))
        self.assertRedirects(resp, '/admin/login/?next=/users')

        self.client.login(username='testuser', password='12345')
        resp = self.client.get(reverse('core:users_map'))
        self.assertRedirects(resp, '/admin/login/?next=/users')

        self.client.login(username='testadmin', password='12345')
        resp = self.client.get(reverse('core:users_map'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'users_map.html')
