import json
from datetime import timezone, datetime, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_disbursements.models import Disbursement
from inventory_logger.models import Log, Action
from items.models import Item

USERNAME = 'test'
PASSWORD = 'testPassword'

TEST_USERNAME = 'ankit'
TEST_PASSWORD = 'lol'


class DisbursementAPITest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        self.receiver = User.objects.create_user(TEST_USERNAME, 'test@test.com', TEST_PASSWORD)
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
        Action.objects.create(color='1', tag='DISBURSED')
        self.item = Item.objects.create(name='lol_item', quantity=50)
        Disbursement.objects.create(disburser=self.admin, item=self.item, quantity=2, receiver=self.receiver, comment='Lol')

    def equalDisbursement(self, disbursement_id, data):
        disbursement_item = Disbursement.objects.get(pk=disbursement_id)
        self.assertEqual(disbursement_item.quantity, data.get("quantity"))
        self.assertEqual(disbursement_item.item.id, data.get("item_id"))
        self.assertEqual(disbursement_item.disburser.id, self.admin.id)
        self.assertEqual(disbursement_item.receiver.id, data.get('receiver_id'))

    def test_create_disbursement(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-list')
        data = {"quantity": 3, "item_id": self.item.id, "comment": "hello", "receiver_id": self.receiver.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        disbursement_json = json.loads(str(response.content, 'utf-8'))
        self.equalDisbursement(disbursement_json.get('id'), data)

    def test_fail_disbursement(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-list')
        data = {"quantity": 40000, "item_id": self.item.id, "comment": "hello", "receiver_id": self.receiver.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_disbursement(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('disbursement-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_disburse_list = json.loads(str(response.content, 'utf-8'))['results']
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Disbursement.objects.count())
        [self.equalDisbursement(json_disburse.get('id'), json_disburse) for json_disburse in json_disburse_list]







