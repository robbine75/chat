from django.contrib.auth.models import User
from django.test import TestCase


class ChatAdminTest(TestCase):
    def setUp(self):
        # Create admin user.
        test_admin = User.objects.create_superuser(
            username='testadmin',
            email='myemail@test.com',
            password='12345'
        )
        test_admin.save()

    def test_admin_message(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/core/message/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/core/message/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_profile(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/core/profile/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/core/profile/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

        resp = self.client.get('/admin/core/profile/1/change/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_thread(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/core/thread/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/core/thread/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_unreadthread(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/core/unreadthread/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/core/unreadthread/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_friendshiprequest(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/core/friendshiprequest/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/core/friendshiprequest/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')

    def test_admin_friend(self):
        self.client.login(username='testadmin', password='12345')
        resp = self.client.get('/admin/core/friend/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/base.html')

        resp = self.client.get('/admin/core/friend/add/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'admin/change_form.html')
