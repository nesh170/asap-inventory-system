import json

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from items.models import Item

USERNAME = 'test'
PASSWORD = 'testPassword'


def equal_item(test_client, item_json, item_id):
    item = Item.objects.get(pk=item_id)
    test_client.assertEqual(item_json.get('name'), item.name)
    test_client.assertEqual(item_json.get('quantity'), item.quantity)
    test_client.assertEqual(item_json.get('model_number'), item.model_number)
    test_client.assertEqual(item_json.get('description'), item.description)
    test_client.assertEqual(item_json.get('location'), item.location)
    test_client.assertEqual([tagItem['tag'] for tagItem in item_json.get('tags', [])],
                            [tag_item.tag for tag_item in item.tags.all()])


class GetItemTestCase(APITestCase):
    def setUp(self):
        User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        item_with_one_tag = Item.objects.create(name="quad 2-input NAND gate", quantity=0, model_number="48979",
                                                description="Jameco", location="hudson 116")
        item_with_one_tag.tags.create(tag="test")
        basic_item = Item.objects.create(name="Oscilloscope", quantity=3)

    def test_get_items(self):
        url = reverse('item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_item_list = json.loads(str(response.content, 'utf-8'))['results']
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Item.objects.count())
        [equal_item(self, json_item, json_item.get('id')) for json_item in json_item_list]


    def test_get_detailed_view(self):
        for item_id_obj in Item.objects.values_list('id'):
            item_id = item_id_obj[0]
            url = reverse(viewname='item-detail', kwargs={'pk': str(item_id)})
            response = self.client.get(url)
            equal_item(self, json.loads(str(response.content, 'utf-8')), item_id)


class PostItemTestCase(APITestCase):
    def setUp(self):
        User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)

    def test_post_items_with_tags(self):
        url = reverse('item-list')
        data = {'name': 'resistors', 'quantity': 10, 'tags': [{'tag': 'bottle'}, {'tag': 'tom'}]}
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_item = json.loads(str(response.content, 'utf-8'))
        equal_item(self, data, json_item.get('id'))
        self.client.logout()

    def test_post_items_with_no_tags(self):
        url = reverse('item-list')
        data = {'name': 'Arduino Uno', 'quantity': 3}
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_item = json.loads(str(response.content, 'utf-8'))
        equal_item(self, data, json_item.get('id'))
        self.client.logout()

class UpdateItemTestCase(APITestCase):
    def setUp(self):
        User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        basic_item = Item.objects.create(name="Capacitor", quantity=9000)
        self.item_id = basic_item.id

    def test_update_all(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
        data = {'name': 'Electrolytic Capacitor', 'quantity': 2, 'model_number': '4',
                'description': 'lol', 'location': 'tom'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = Item.objects.get(pk=json.loads(str(response.content, 'utf-8')).get('id'))
        self.assertEqual(data.get('name'),item.name)
        self.assertEqual(data.get('quantity'), item.quantity)
        self.assertEqual(data.get('model_number'), item.model_number)
        self.assertEqual(data.get('description'), item.description)
        self.assertEqual(data.get('location'), item.location)
        self.client.logout()

    def test_update_name(self):
        self.client.login(username=USERNAME, password=PASSWORD)
        url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
        data = {'name': 'Cryogenic Freezer'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = Item.objects.get(pk=json.loads(str(response.content, 'utf-8')).get('id'))
        self.assertEqual(data.get('name'), item.name)
        self.client.logout()


class DeleteItemTestCase(APITestCase):
        def setUp(self):
            User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
            basic_item = Item.objects.create(name="Cryogenic", quantity=9000)
            self.item_id = basic_item.id

        def test_delete(self):
            self.client.login(username=USERNAME, password=PASSWORD)
            url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            delete_success = False
            try:
                Item.objects.get(pk=self.item_id)
            except ObjectDoesNotExist:
                delete_success = True
            self.assertEqual(delete_success, True)
