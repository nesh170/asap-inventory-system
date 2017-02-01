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
from items.models import Item, Tag

USERNAME = 'test'
PASSWORD = 'testPassword'


class CreateDeleteTagTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        basic_item = Item.objects.create(name="tourniquet", quantity=4)
        self.item_id = basic_item.id
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

    def test_create_tag(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('tag-creation')
        data = {'item': self.item_id, 'tag': 'pain'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = Item.objects.get(pk = self.item_id)
        self.assertEqual(item.tags.first().tag, data.get('tag'))

    def test_delete_tag(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        tag = Item.objects.get(pk=self.item_id).tags.create(tag='lol')
        url = reverse(viewname='tag-deletion', kwargs={'pk': str(tag.id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        delete_success = False
        try:
            Tag.objects.get(pk=tag.id)
        except ObjectDoesNotExist:
            delete_success = True
        self.assertEqual(delete_success, True)



