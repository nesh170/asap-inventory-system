import json
from datetime import timedelta, timezone, datetime

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_logger.models import Action
from items.models import Item

USERNAME = 'test'
PASSWORD = 'testPassword'
STAFF_USERNAME = 'staff'
STAFF_PASSWORD = 'password'


def equal_item(test_client, item_json, item_id):
    item = Item.objects.get(pk=item_id)
    test_client.assertEqual(item_json.get('name'), item.name)
    test_client.assertEqual(item_json.get('quantity'), item.quantity)
    test_client.assertEqual(item_json.get('model_number'), item.model_number)
    test_client.assertEqual(item_json.get('description'), item.description)
    if item_json.get('tags') is not None:
        test_client.assertEqual([tagItem['tag'] for tagItem in item_json.get('tags', [])],
                                [tag_item.tag for tag_item in item.tags.all()])


class GetItemTestCase(APITestCase):
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']

        item_with_one_tag = Item.objects.create(name="quad 2-input NAND gate", quantity=0, model_number="48979",
                                                description="Jameco")
        item_with_one_tag.tags.create(tag="test")
        basic_item = Item.objects.create(name="Oscilloscope", quantity=3)
        Action.objects.create(color='1', tag='ITEM CREATED')
        Action.objects.create(color='2', tag='ITEM DESTROYED')
        Action.objects.create(color='3', tag='ITEM MODIFIED')

    def test_get_items(self):
        url = reverse('item-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_item_list = json.loads(str(response.content, 'utf-8'))['results']
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Item.objects.count())
        [equal_item(self, json_item, json_item.get('id')) for json_item in json_item_list]

    def test_get_detailed_view(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        for item_id_obj in Item.objects.values_list('id'):
            item_id = item_id_obj[0]
            url = reverse(viewname='item-detail', kwargs={'pk': str(item_id)})
            response = self.client.get(url)
            equal_item(self, json.loads(str(response.content, 'utf-8')), item_id)

    def test_get_unique_list(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('unique-item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_item_list = json.loads(str(response.content, 'utf-8'))['results']
        item_list = set([item.get('name') for item in json_item_list])
        correct_item_list = set([item_name for item_name in Item.objects.all().values_list('name', flat=True).distinct()])
        self.assertEqual(item_list, correct_item_list)


class PostItemTestCase(APITestCase):
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
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']
        Action.objects.create(color='1', tag='ITEM CREATED')
        Action.objects.create(color='2', tag='ITEM DESTROYED')
        Action.objects.create(color='3', tag='ITEM MODIFIED')

    def test_post_items_with_tags(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('item-list')
        data = {'name': 'resistors', 'quantity': 10, 'tags': [{'tag': 'bottle'}, {'tag': 'tom'}]}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_item = json.loads(str(response.content, 'utf-8'))
        equal_item(self, data, json_item.get('id'))

    def test_post_items_with_no_tags(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('item-list')
        data = {'name': 'Arduino Uno', 'quantity': 3}
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_item = json.loads(str(response.content, 'utf-8'))
        equal_item(self, data, json_item.get('id'))

    def test_post_items_with_null_tags(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('item-list')
        data = {'name': 'Hybrid Engine', 'quantity': 3, 'tags': None}
        self.client.login(username=USERNAME, password=PASSWORD)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_item = json.loads(str(response.content, 'utf-8'))
        equal_item(self, data, json_item.get('id'))


class UpdateItemTestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        basic_item = Item.objects.create(name="Capacitor", quantity=9000)
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
        self.staff = User.objects.create_user(username=STAFF_USERNAME,password=STAFF_PASSWORD,is_staff=True)
        self.staff_application = Application(
            name="Test_Staff Application",
            redirect_uris="http://localhost",
            user=self.staff,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.staff_application.save()
        self.staff_tok = AccessToken.objects.create(
            user=self.staff, token='1234567890123',
            application=self.staff_application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )
        oauth2_settings._DEFAULT_SCOPES = ['read','write','groups']
        Action.objects.create(color='1', tag='ITEM CREATED')
        Action.objects.create(color='2', tag='ITEM DESTROYED')
        Action.objects.create(color='3', tag='ITEM MODIFIED')

    def test_update_quantity_using_staff(self):
        self.client.force_authenticate(user=self.staff, token=self.staff_tok)
        item = Item.objects.get(pk=self.item_id)
        url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
        data = {'quantity': 2, 'name': "lit"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(json.loads(str(response.content, 'utf-8')).get('detail'),
                         "Staff/Managers are not allowed to change the quantity")
        item_updated = Item.objects.get(pk=self.item_id)
        self.assertEqual(item.name, item_updated.name)
        self.assertEqual(item.quantity, item_updated.quantity)


    def test_update_all_using_staff(self):
        self.client.force_authenticate(user=self.staff, token=self.staff_tok)
        url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
        data = {'name': 'Light Rails Capacitor', 'model_number': '412343',
                'description': 'lol'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = Item.objects.get(pk=json.loads(str(response.content, 'utf-8')).get('id'))
        self.assertEqual(data.get('name'), item.name)
        self.assertEqual(data.get('model_number'), item.model_number)
        self.assertEqual(data.get('description'), item.description)

    def test_update_all(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
        data = {'name': 'Electrolytic Capacitor', 'quantity': 2, 'model_number': '4',
                'description': 'lol'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = Item.objects.get(pk=json.loads(str(response.content, 'utf-8')).get('id'))
        self.assertEqual(data.get('name'),item.name)
        self.assertEqual(data.get('quantity'), item.quantity)
        self.assertEqual(data.get('model_number'), item.model_number)
        self.assertEqual(data.get('description'), item.description)

    def test_update_name(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
        data = {'name': 'Cryogenic Freezer'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = Item.objects.get(pk=json.loads(str(response.content, 'utf-8')).get('id'))
        self.assertEqual(data.get('name'), item.name)

    def test_log_addition_acquisitions_item_not_found(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='item-quantity-modification')
        data = {'item_id': 10234, 'quantity': 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_log_addition_acquisitions_quantity_is_zero(self):
        item = Item.objects.create(name='Replication gun', quantity=100)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='item-quantity-modification')
        data = {'item_id': item.id, 'quantity': 0}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_log_destruction_more_than_avaliable(self):
        item = Item.objects.create(name='Pulsear gun', quantity=100)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='item-quantity-modification')
        data = {'item_id': item.id, 'quantity': -1000}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_log_addition_acquisitions(self):
        item = Item.objects.create(name='Magnetic Accelerated Cannon', quantity=100)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse(viewname='item-quantity-modification')
        data = {'item_id': item.id, 'quantity': 10}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_item = Item.objects.get(pk=item.id)
        self.assertEqual(updated_item.quantity, item.quantity + data.get('quantity'))


class DeleteItemTestCase(APITestCase):
        def setUp(self):
            self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
            basic_item = Item.objects.create(name="Cryogenic", quantity=9000)
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
            Action.objects.create(color='1', tag='ITEM CREATED')
            Action.objects.create(color='2', tag='ITEM DESTROYED')
            Action.objects.create(color='3', tag='ITEM MODIFIED')

        def test_delete(self):
            self.client.force_authenticate(user=self.admin, token=self.tok)
            url = reverse(viewname='item-detail', kwargs={'pk': self.item_id})
            response = self.client.delete(url)
            self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
            delete_success = False
            try:
                Item.objects.get(pk=self.item_id)
            except ObjectDoesNotExist:
                delete_success = True
            self.assertEqual(delete_success, True)
