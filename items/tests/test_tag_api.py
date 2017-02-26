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

from items.models import Item, Tag

USERNAME = 'test'
PASSWORD = 'testPassword'


class CreateDeleteTagTestCase(APITestCase):
    fixtures = ['action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        basic_item = Item.objects.create(name="fire", quantity=4)
        test_item = Item.objects.create(name="tourniquet", quantity=4)
        self.item_id = test_item.id
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
        basic_item.tags.create(tag='lol')
        basic_item.tags.create(tag='lit')
        item = Item.objects.create(name="play", quantity=4)
        item.tags.create(tag='lol')

    def test_create_tag(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('tag-list')
        data = {'item': self.item_id, 'tag': 'pain'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = Item.objects.get(pk=self.item_id)
        self.assertEqual(item.tags.first().tag, data.get('tag'))

    def test_delete_tag(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        tag = Item.objects.get(pk=self.item_id).tags.create(tag='pulsar')
        url = reverse(viewname='tag-deletion', kwargs={'pk': str(tag.id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        delete_success = False
        try:
            Tag.objects.get(pk=tag.id)
        except ObjectDoesNotExist:
            delete_success = True
        self.assertEqual(delete_success, True)

    def test_get_distinct_tag(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('unique-tag-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_object = json.loads(str(response.content, 'utf-8')).get('results')
        tag_list = [tag.get('tag') for tag in json_object]
        correct_tag_list = [tag for tag in Tag.objects.all().values_list('tag', flat=True).distinct()]
        self.assertEqual(correct_tag_list, tag_list)