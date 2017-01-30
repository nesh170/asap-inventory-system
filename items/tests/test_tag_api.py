import json

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from items.models import Item, Tag

USERNAME = 'test'
PASSWORD = 'testPassword'


class CreateDeleteTagTestCase(APITestCase):
    def setUp(self):
        User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        basic_item = Item.objects.create(name="tourniquet", quantity=4)
        self.item_id = basic_item.id

    def test_create_tag(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        url = reverse('tag-creation')
        data = {'item': self.item_id, 'tag': 'pain'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        item = Item.objects.get(pk = self.item_id)
        self.assertEqual(item.tags.first().tag, data.get('tag'))
        self.client.logout()

    def test_delete_tag(self):
        self.client.login(username=USERNAME, password=PASSWORD)
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
        self.client.logout()



