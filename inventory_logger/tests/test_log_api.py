import json
from datetime import timezone, datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from inventory_logger.models import Log

USERNAME = 'test'
PASSWORD = 'testPassword'


class CreateDeleteTagTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
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

    def test_create_log(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('log-list')
        data = {'action': 'disperse', 'description': 'disperse a number of micro stars'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        log_json = json.loads(str(response.content, 'utf-8'))
        log = Log.objects.get(pk=log_json.get('id'))
        self.assertEqual(log.user, USERNAME)
        self.assertEqual(log.action, data.get('action'))
        self.assertEqual(log.description, data.get('description'))




