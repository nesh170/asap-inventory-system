import json
from datetime import timezone, datetime, timedelta

from django.contrib.auth.models import User
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_requests.models import RequestCart
from inventory_transaction_logger.action_enum import ActionEnum
from inventory_transaction_logger.models import Log
from inventory_transaction_logger.utility.logger import LoggerUtility

from items.models.item_models import Item

ADMIN_USERNAME = 'test'
ADMIN_PASSWORD = 'testPassword'

USER_USERNAME = 'user'
USER_PASSWORD = 'masalaPassword'


def equal_cart(test_client, cart_data, log):
    cart = log.request_cart_log.get(pk=cart_data.get('id')).request_cart
    requests_data = cart_data.get('request_cart')
    test_client.assertEqual(cart.id, requests_data.get('id'))


def equal_item(test_client, item_data, log):
    item = log.item_log.get(pk=item_data.get('id')).item
    item_data = item_data.get('item')
    test_client.assertEqual(item.id, item_data.get('id'))


def equal_log(test_client, data, log_id):
    log = Log.objects.get(pk=log_id)
    test_client.assertEqual(log.initiating_user.username, data.get('initiating_user'))
    if data.get('affected_user') is not None:
        test_client.assertEqual(log.affected_user.username, data.get('affected_user'))
    nature_data = data.get("nature")
    test_client.assertEqual(log.nature.tag, nature_data.get("tag"))
    if data.get("request_cart_log") is not None:
        [equal_cart(test_client, cart_data, log) for cart_data in data.get("request_cart_log")]
    if data.get("item_log") is not None:
        [equal_item(test_client, item_data, log) for item_data in data.get("item_log")]


class LogTestCase(APITestCase):
    fixtures = ['logger_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(ADMIN_USERNAME, '', ADMIN_PASSWORD)
        self.normal_user = User.objects.create_user(USER_USERNAME, '', USER_PASSWORD)
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
        item_with_one_tag = Item.objects.create(name="oscilloscope", quantity=3, model_number="48979",
                                                description="oscilloscope")
        item_with_one_tag.tags.create(tag="test")
        item_with_zero_tags = Item.objects.create(name="resistor", quantity=50, model_number="1234", description="resistor")
        items_affected = [item_with_one_tag, item_with_zero_tags]
        request = RequestCart.objects.create(owner=self.normal_user, status="active", reason="test shopping cart",
                                             staff_comment="this is an admin comment", staff=self.admin)
        another_request = RequestCart.objects.create(owner=self.admin, status="outstanding", reason="another shopping cart",
                                                     staff_comment="hi", staff=self.admin)
        requests_affected = [request, another_request]
        LoggerUtility.log(self.admin, ActionEnum.ITEM_CREATED,  "This is creating a request", self.normal_user,
                          items_affected, requests_affected)

    def test_get_logs(self):
        url = reverse('log-list')
        self.client.force_authenticate(user=self.admin, token=self.tok)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # converts response to a string and then to a JSON dictionary, and then gets results attribute of it
        json_request_list = json.loads(str(response.content, 'utf-8'))['results']
        [equal_log(self, json_request, json_request.get('id')) for json_request in json_request_list]

    def test_get_detailed_log(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        for log_id in Log.objects.values_list('id', flat=True):
            url = reverse('detailed-log', kwargs={'pk': str(log_id)})
            # make the get request
            response = self.client.get(url)
            # compare the JSON response received from the GET request to what is in database
            equal_log(self, json.loads(str(response.content, 'utf-8')), log_id)