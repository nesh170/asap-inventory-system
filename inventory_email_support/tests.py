# username and password to create superuser for testing
import json
from datetime import datetime, timezone, timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from oauth2_provider.admin import Application
from oauth2_provider.models import AccessToken
from oauth2_provider.settings import oauth2_settings
from rest_framework import status
from rest_framework.test import APITestCase

from inventory_email_support.models import SubscribedManagers, SubjectTag
from inventory_requests.models import RequestCart, Loan
from items.models import Item

USERNAME = 'admin'
PASSWORD = 'adminPassword'
TEST_USERNAME = 'test_user'
TEST_PASSWORD = 'testPassword'


def equal_subscribed_manager(test_client, subscribed_manager_json, subscribed_manager_id, user_id):
    subscribed_manager = SubscribedManagers.objects.get(pk=subscribed_manager_id)
    test_client.assertEqual(subscribed_manager_json.get('member').get('username'), subscribed_manager.member.username)
    test_client.assertEqual(subscribed_manager_json.get('member').get('email'), subscribed_manager.member.email)
    test_client.assertEqual(subscribed_manager.member.id, user_id)

def equal_subject_tag(test_client, subject_tag_json, subject_tag_id):
    subject_tag_db = SubjectTag.objects.get(pk=subject_tag_id)
    test_client.assertEqual(subject_tag_json.get('subject_tag'), subject_tag_db.subject_tag)

class EmailTestCases(APITestCase):
    fixtures = ['requests_action.json']

    def setUp(self):
        self.admin = User.objects.create_superuser(USERNAME, 'test@test.com', PASSWORD)
        self.basic_user = User.objects.create_user(TEST_USERNAME, 'test@test.com', TEST_PASSWORD)

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
        self.test_application = Application(
            name="Test User Application",
            redirect_uris="http://localhost",
            user=self.basic_user,
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
        )
        self.test_application.save()
        self.test_tok = AccessToken.objects.create(
            user=self.basic_user, token='123490',
            application=self.test_application, scope='read write',
            expires=datetime.now(timezone.utc) + timedelta(days=30)
        )
        oauth2_settings._DEFAULT_SCOPES = ['read', 'write', 'groups']
        self.item = Item.objects.create(name="test_item_1", quantity=10)
        self.item_1 = Item.objects.create(name="test item 2", quantity=4)

    def test_get_all_subscribed_managers(self):
        subscribed_manager = SubscribedManagers.objects.create(member=self.admin)
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('subscribed-manager-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], SubscribedManagers.objects.count())
        subscribed_managers_json = json.loads(str(response.content, 'utf-8'))['results']
        [equal_subscribed_manager(self, subscribed_manager_json, subscribed_manager_json.get('id'), self.admin.id)
         for subscribed_manager_json in subscribed_managers_json]

    def test_subscribe(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('subscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(str(response.content, 'utf-8'))
        equal_subscribed_manager(self, json_response, json_response.get('id'), self.admin.id)

    def test_subscribe_fail_already_subscribed(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('subscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = json.loads(str(response.content, 'utf-8'))
        second_response = self.client.post(url)
        self.assertEqual(second_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(SubscribedManagers.objects.filter(id=json_response.get('id')).count(), 1)


    def test_unsubscribe(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        subscribed_manager = SubscribedManagers.objects.create(member=self.admin)
        url = reverse('unsubscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        unsubscribe_success = False
        try:
            SubscribedManagers.objects.get(member=self.admin)
        except ObjectDoesNotExist:
            unsubscribe_success = True
        self.assertEqual(unsubscribe_success, True)


    def test_unsubscribe_fail_not_exists(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('unsubscribe')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        json_response = json.loads(str(response.content, 'utf-8'))
        unsubscribe_fail = False
        try:
            SubscribedManagers.objects.get(member=self.admin)
        except ObjectDoesNotExist:
            unsubscribe_fail = True
        self.assertEqual(unsubscribe_fail, True)

    def test_get_subject_tag(self):
        SubjectTag.objects.create(subject_tag="this is a subject tag")
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('get-subject-tag')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], SubjectTag.objects.count())

        subject_tags_json = json.loads(str(response.content, 'utf-8'))['results']
        [equal_subject_tag(self, subject_tag_json, subject_tag_json.get('id')) for subject_tag_json in subject_tags_json]

    # def test_get_all_loans(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, reason="test shopping cart")
    #     cart.cart_loans.create(item=self.item, quantity=2)
    #     cart.cart_loans.create(item=self.item_1, quantity=4)
    #     url = reverse('add-loan-to-cart')
    #     self.client.force_authenticate(user=self.admin, token=self.tok)
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], Loan.objects.count())
    #     loans_json = json.loads(str(response.content, 'utf-8'))['results']
    #     [equal_loans(self, loan_json, loan_json['id']) for loan_json in loans_json]
    #     cart.delete()
    #
    # def test_create_loan_fail_inactive_cart(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, status='fulfilled', reason="test")
    #     self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
    #     url = reverse('add-loan-to-cart')
    #     data = {'item_id': self.item.id, 'quantity': 10}
    #     response = self.client.post(path=url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], "Item must be added to active cart")
    #     cart.delete()
    #
    # def test_create_loan(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, reason="test shopping cart")
    #     self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
    #     url = reverse('add-loan-to-cart')
    #     data = {'item_id':self.item.id, 'quantity': 10}
    #     response = self.client.post(path=url, data=data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     loan_json = json.loads(str(response.content, 'utf-8'))
    #     equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'], cart_id=cart.id)
    #     cart.delete()
    #
    # def test_delete_loan_inactive_cart(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, status='fulfilled', reason="test")
    #     loan = Loan.objects.create(item=self.item_1, quantity=10, cart=cart)
    #     self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
    #     url = reverse('delete-loan-from-cart',  kwargs={'pk': str(loan.id)})
    #     response = self.client.delete(path=url)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
    #                      "Cannot delete loan as request status: fulfilled != active")
    #     self.assertTrue(Loan.objects.filter(pk=loan.id).exists())
    #
    # def test_delete_loan(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, reason="active cart is lit")
    #     loan = Loan.objects.create(item=self.item_1, quantity=10, cart=cart)
    #     self.client.force_authenticate(user=self.basic_user, token=self.test_tok)
    #     url = reverse('delete-loan-from-cart',  kwargs={'pk': str(loan.id)})
    #     response = self.client.delete(path=url)
    #     self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    #     self.assertFalse(Loan.objects.filter(pk=loan.id).exists())
    #     cart.delete()
    #
    # def test_return_loan_unfulfilled_cart(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, status='active', reason="test")
    #     loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
    #     self.client.force_authenticate(user=self.admin, token=self.tok)
    #     url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
    #     response = self.client.patch(path=url)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     detail_str = "Request needs to be fulfilled but is {status} and {item_name} cannot be " \
    #                  "returned already by {user_name}".format(status=cart.status, item_name=self.item_1.name,
    #                                                           user_name=self.basic_user.username)
    #     self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'], detail_str)
    #     self.assertTrue(Loan.objects.filter(pk=loan.id).exists())
    #     cart.delete()
    #
    # def test_return_loan(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
    #     loan = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
    #     self.item_1.quantity = self.item_1.quantity - loan.quantity
    #     self.item_1.save()
    #     self.client.force_authenticate(user=self.admin, token=self.tok)
    #     url = reverse('return-loan-from-cart', kwargs={'pk': str(loan.id)})
    #     response = self.client.patch(path=url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     loan_json = json.loads(str(response.content, 'utf-8'))
    #     equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'])
    #     updated_loan = Loan.objects.get(pk=loan.id)
    #     updated_item = Item.objects.get(pk=self.item_1.id)
    #     self.assertEqual(updated_item.quantity, self.item_1.quantity + loan.quantity)
    #     self.assertTrue(updated_loan.returned_timestamp > updated_loan.loaned_timestamp)
    #     cart.delete()
    #
    # def test_return_all_loans_fully_returned_fail(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
    #     loan = Loan.objects.create(item=self.item, quantity=1, cart=cart, loaned_timestamp=datetime.now(),
    #                                returned_timestamp=datetime.now())
    #     self.item.quantity = self.item.quantity - loan.quantity
    #     self.item.save()
    #     self.client.force_authenticate(user=self.admin, token=self.tok)
    #     url = reverse('return-all-loans-from-cart', kwargs={'pk': str(cart.id)})
    #     response = self.client.patch(path=url)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     self.assertEqual(json.loads(str(response.content, 'utf-8'))['detail'],
    #                      "Request needs to be fulfilled but is fulfilled or Cart has been fully returned")
    #
    # def test_return_all_loans(self):
    #     cart = RequestCart.objects.create(owner=self.basic_user, status="fulfilled", reason="return loan cart")
    #     loan = Loan.objects.create(item=self.item, quantity=1, cart=cart, loaned_timestamp=datetime.now())
    #     loan_1 = Loan.objects.create(item=self.item_1, quantity=4, cart=cart, loaned_timestamp=datetime.now())
    #     self.item.quantity = self.item.quantity - loan.quantity
    #     self.item.save()
    #     self.item_1.quantity = self.item_1.quantity - loan_1.quantity
    #     self.item_1.save()
    #     self.client.force_authenticate(user=self.admin, token=self.tok)
    #     url = reverse('return-all-loans-from-cart', kwargs={'pk': str(cart.id)})
    #     response = self.client.patch(path=url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     cart_id = json.loads(str(response.content, 'utf-8'))['id']
    #     loans_json = json.loads(str(response.content, 'utf-8'))['cart_loans']
    #     [equal_loans(test_client=self, loan_json=loan_json, loan_id=loan_json['id'], cart_id=cart_id)
    #      for loan_json in loans_json]
    #     [self.assertTrue(Loan.objects.get(pk=loan_json['id']).returned_timestamp is not None)
    #      for loan_json in loans_json]
    #     cart.delete()
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
