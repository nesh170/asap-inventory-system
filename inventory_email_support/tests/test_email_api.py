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

from inventory_email_support.models import SubscribedManagers, SubjectTag, PrependedBody, LoanReminderSchedule
from items.models import Item
from datetime import date

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


def equal_prepended_body(test_client, prepended_body_json, prepended_body_id):
    prepended_body_db = PrependedBody.objects.get(pk=prepended_body_id)
    test_client.assertEqual(prepended_body_json.get('prepended_body'), prepended_body_db.prepended_body)


def equal_loan_reminder(test_client, loan_reminder_json, loan_reminder_id):
    loan_reminder_db = LoanReminderSchedule.objects.get(pk=loan_reminder_id)
    test_client.assertEqual(loan_reminder_json.get('date'), str(loan_reminder_db.date))
    test_client.assertEqual(loan_reminder_json.get('executed'), loan_reminder_db.executed)


class EmailTestCases(APITestCase):

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
        subject_tag_json = json.loads(str(response.content, 'utf-8'))
        equal_subject_tag(self, subject_tag_json, subject_tag_json.get('id'))

    def test_modify_subject_tag_db_populated(self):
        SubjectTag.objects.create(subject_tag="this is a subject tag")
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('modify-subject-tag')
        data = {'subject_tag': 'modified subject tag'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SubjectTag.objects.count(), 1)
        json_response = json.loads(str(response.content, 'utf-8'))
        equal_subject_tag(self, json_response, json_response.get('id'))

    def test_modify_subject_tag_not_db_populated(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('modify-subject-tag')
        data = {'subject_tag': 'new subject tag'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(SubjectTag.objects.count(), 1)
        json_response = json.loads(str(response.content, 'utf-8'))
        equal_subject_tag(self, json_response, json_response.get('id'))

    def test_get_prepended_body(self):
        PrependedBody.objects.create(prepended_body="this is a prepended body")
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('get-prepended-body')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prepended_body_json = json.loads(str(response.content, 'utf-8'))
        equal_prepended_body(self, prepended_body_json, prepended_body_json.get('id'))

    def test_modify_prepended_body_db_populated(self):
        PrependedBody.objects.create(prepended_body="this is a prepended body")
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('modify-prepended-body')
        data = {'prepended_body': 'modified prepended body'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PrependedBody.objects.count(), 1)
        json_response = json.loads(str(response.content, 'utf-8'))
        equal_prepended_body(self, json_response, json_response.get('id'))

    def test_modify_prepended_body_not_db_populated(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('modify-prepended-body')
        data = {'prepended_body': 'new prepended body'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PrependedBody.objects.count(), 1)
        json_response = json.loads(str(response.content, 'utf-8'))
        equal_prepended_body(self, json_response, json_response.get('id'))

    def test_get_all_loan_reminder_dates(self):
        loan_reminder_date = LoanReminderSchedule.objects.create(date=date(2017, 3, 25))
        self.client.force_authenticate(user=self.admin, token=self.tok)
        url = reverse('get-loan-reminder-dates')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print(json.loads(str(response.content, 'utf-8')))
        self.assertEqual(json.loads(str(response.content, 'utf-8'))['count'], LoanReminderSchedule.objects.count())
        loan_reminders_json = json.loads(str(response.content, 'utf-8'))['results']
        [equal_loan_reminder(self, loan_reminder_json, loan_reminder_json.get('id'))
         for loan_reminder_json in loan_reminders_json]

    def test_loan_reminder_date_before_today_fail(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = [{"date": "2015-3-24"}]
        url = reverse('modify-loan-reminder-dates')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        loan_reminder_date_add_fail = False
        try:
            LoanReminderSchedule.objects.get(date=date(2015, 3, 24))
        except ObjectDoesNotExist:
            loan_reminder_date_add_fail = True
        self.assertEqual(loan_reminder_date_add_fail, True)

    def test_loan_reminder_multiple_dates(self):
        self.client.force_authenticate(user=self.admin, token=self.tok)
        data = [{"date": "2017-4-25"}, {"date": "2017-4-27"}]
        url = reverse('modify-loan-reminder-dates')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan_reminders_json = json.loads(str(response.content, 'utf-8'))
        [equal_loan_reminder(self, loan_reminder_json, loan_reminder_json.get('id'))
         for loan_reminder_json in loan_reminders_json]
