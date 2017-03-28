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

from items.models import Item, Field, LongTextField, ShortTextField, IntField, FloatField

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password'


class FieldsAPI(APITestCase):
    fixtures = ['item_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
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
        int_field_private = Field.objects.create(name='int_val_private', type='integer', private=True)
        int_field_regular = Field.objects.create(name='int_val_regular', type='integer', private=False)
        float_field_private = Field.objects.create(name='float_val_private', type='float', private=True)
        float_field_regular = Field.objects.create(name='float_val_regular', type='float', private=False)
        short_text_field_private = Field.objects.create(name='short_text_val_private', type='short_text', private=True)
        short_text_field_regular = Field.objects.create(name='short_text_val_regular', type='short_text', private=False)
        long_text_field_private = Field.objects.create(name='long_text_val_private', type='long_text', private=True)
        long_text_field_regular = Field.objects.create(name='long_text_val_regular', type='long_text', private=False)
        self.item = Item.objects.create(name="quad 2-input NAND gate", quantity=0, model_number="48979",
                                                description="Jameco")
        self.item.int_fields.create(field=int_field_private,value=10)
        self.item.int_fields.create(field=int_field_regular, value=11)
        self.item.float_fields.create(field=float_field_private, value=10.54)
        self.item.float_fields.create(field=float_field_regular, value=1111.2)
        self.item.short_text_fields.create(field=short_text_field_private, value="Greatest of all time")
        self.item.short_text_fields.create(field=short_text_field_regular, value="Has got a nice ring to it")
        self.item.long_text_fields.create(field=long_text_field_private, value="I'm on a level that your elevator can't reach")
        self.item.long_text_fields.create(field=long_text_field_regular, value="I got information that your school system doesn't teach")

    def test_get_fields(self):
        url = reverse('field-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_field_list = json.loads(str(response.content, 'utf-8'))['results']
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Field.objects.count())
        for json_field in json_field_list:
            field = Field.objects.get(pk=json_field.get('id'))
            self.assertEqual(json_field.get('name'), field.name)
            self.assertEqual(json_field.get('type'), field.type)
            self.assertEqual(json_field.get('private'), field.private)

    def test_post_fields(self):
        url = reverse('field-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"name": "lit_int_field", "type": "float", "private": False}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_field = json.loads(str(response.content, 'utf-8'))
        field_created = Field.objects.get(pk=json_field.get('id'))
        self.assertEqual(data.get('name'), field_created.name)
        self.assertEqual(data.get('type'), field_created.type)
        self.assertEqual(data.get('private'), field_created.private)
        self.assertEqual(field_created.floats.get(item=self.item), self.item.float_fields.get(field=field_created))

    def test_patch_field_unsuccessful_type_change(self):
        field = Field.objects.create(name='lol', type='float', private=False)
        url = reverse('field-detail', kwargs={'pk': str(field.id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"name": "lolz_fire", "type": "int", "private": True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        error_json = json.loads(str(response.content, 'utf-8'))
        self.assertEqual(error_json.get('detail'), "You cannot change the type of a field")

    def test_patch_fields(self):
        field = Field.objects.create(name='lol', type='float', private=False)
        url = reverse('field-detail', kwargs={'pk': str(field.id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"name": "lolz_fire", "private": True}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_field = json.loads(str(response.content, 'utf-8'))
        field_created = Field.objects.get(pk=json_field.get('id'))
        self.assertEqual(data.get('name'), field_created.name)
        self.assertEqual(data.get('private'), field_created.private)

    def test_patch_long_text_field(self):
        long_field_id = self.item.long_text_fields.first().id
        url = reverse(viewname='long-text-field-update', kwargs={'pk': str(long_field_id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"value": "Login is true bae"}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(LongTextField.objects.get(pk=long_field_id).value, data.get("value"))

    def test_patch_short_text_field(self):
        short_field_id = self.item.short_text_fields.first().id
        url = reverse(viewname='short-text-field-update', kwargs={'pk': str(short_field_id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"value": "short_test_try"}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ShortTextField.objects.get(pk=short_field_id).value, data.get("value"))

    def test_patch_int_field(self):
        int_field_id = self.item.int_fields.first().id
        url = reverse(viewname='int-field-update', kwargs={'pk': str(int_field_id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"value": 1}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(IntField.objects.get(pk=int_field_id).value, data.get("value"))

    def test_patch_float_field(self):
        float_field_id = self.item.float_fields.first().id
        url = reverse(viewname='float-field-update', kwargs={'pk': str(float_field_id)})
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = {"value": 1.123}
        response = self.client.patch(path=url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FloatField.objects.get(pk=float_field_id).value, data.get("value"))

    def test_delete_field(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        field_id = self.item.float_fields.first().field.id
        url = reverse(viewname='field-detail', kwargs={'pk': str(field_id)})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        delete_success = False
        try:
            Field.objects.get(pk=field_id)
        except ObjectDoesNotExist:
            delete_success = True
        self.assertEqual(delete_success, True)





