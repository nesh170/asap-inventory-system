import json
from datetime import timezone, datetime, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

USERNAME = 'test'
PASSWORD = 'testPassword'


def equal_user(equal_client, user_id, data):
    user = User.objects.get(pk=user_id)
    equal_client.assertEqual(user.username, data.get('username'))
    equal_client.assertEqual(user.email, data.get('email'))
    equal_client.assertEqual(user.is_staff, data.get('is_staff'))
    equal_client.assertEqual(user.is_superuser, data.get('is_superuser'))


class UserAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        User.objects.create_superuser('piazza', 'lol@test.com', PASSWORD)
        self.application = Application(
            name="Test Application",
            redirect_uris="http://localhost",
            user=self.admin,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.application.save()
        self.tok = AccessToken.objects.create(
            user=self.admin, token='1234567890',
            application=self.application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )
        oauth2_settings._DEFAULT_SCOPES = ['read', 'write', 'groups']

    def test_create_super_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('user-list')
        data = {'username': 'lol', 'password': 'Biebs4lyfe', 'email': 'sorry@toolate.com', 'is_staff': True,
                'is_superuser': True}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_user = json.loads(str(response.content, 'utf-8'))
        equal_user(self, json_user.get('id'), data)

    def test_create_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('user-list')
        data = {'username': 'powerUp', 'password': 'Biebs4lyfe', 'email': 'sorry@sorrynow.com', 'is_staff': False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_user = json.loads(str(response.content, 'utf-8'))
        data['is_superuser'] = json_user.get('is_superuser')
        equal_user(self, json_user.get('id'), data)

    def test_get_all_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_user_list = json.loads(str(response.content, 'utf-8')).get('results')
        for json_user in json_user_list:
            equal_user(self, json_user.get('id'), json_user)

    def test_get_detailed_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        users = User.objects.all()
        for user in users:
            url = reverse('user-detail', kwargs={'pk': user.id})
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            json_user = json.loads(str(response.content, 'utf-8'))
            equal_user(self, json_user.get('id'), json_user)

    def test_delete_user(self):
        user = User.objects.create_user(username='testlololol', password='firestorm123123', email='git@gitkasld.com')
        url = reverse('user-detail', kwargs={'pk': user.id})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.get(pk=user.id).is_active, False)

    def test_get_current_user(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('user-current')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_user = json.loads(str(response.content, 'utf-8'))
        equal_user(self, json_user.get('id'), json_user)

    def test_get_large_user_list(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('large-user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_user_list = json.loads(str(response.content, 'utf-8'))['results']
        user_list = [user.get('username') for user in json_user_list]
        correct_user_list = [user_name for user_name in User.objects.all().values_list('username', flat=True).distinct()]
        self.assertEqual(set(user_list), set(correct_user_list))

    def test_update_user_is_superuser_staff_not_specificied(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        user = User.objects.create_user(username='lolsadoq', password='ty1892371203', email='nesh@lol.com')
        data = {'is_superuser': True}
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.is_superuser, False)

    def test_update_user_is_superuser_not_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        user = User.objects.create_user(username='lol', password='ty1892371203', email='nesh@lol.com')
        data = {'is_superuser': True, 'is_staff': False}
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.is_superuser, False)

    def test_update_user_is_superuser(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        user = User.objects.create_user(username='lol232', password='ty1892371203', email='nesh@lol.com')
        data = {'is_superuser': True, 'is_staff': True}
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.is_superuser, True)
        self.assertEqual(updated_user.is_staff, True)

    def test_update_user_is_staff_not_superuser(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        user = User.objects.create_user(username='lol232sd1', password='ty1892371203', email='nesh@lol.com')
        data = {'is_staff': True}
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.is_superuser, False)
        self.assertEqual(updated_user.is_staff, False)

    def test_update_user_is_staff(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        user = User.objects.create_user(username='lol232sd1', password='ty1892371203', email='nesh@lol.com')
        data = {'is_staff': True, 'is_superuser': False}
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.is_superuser, False)
        self.assertEqual(updated_user.is_staff, True)

    def test_update_user_email(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        user = User.objects.create_user(username='asd123343', password='ty1892371203', email='nesh@lol.com')
        data = {'email': 'nesh@145.com'}
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = User.objects.get(pk=user.id)
        self.assertEqual(updated_user.email, data.get('email'))
        self.assertEqual(updated_user.is_superuser, user.is_superuser)
        self.assertEqual(updated_user.is_staff, user.is_staff)

