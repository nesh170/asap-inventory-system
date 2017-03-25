from django.conf.urls import url

from inventory_email_support.views.loan_reminder_email_view import GetLoanReminderDates, CreateLoanReminderDates
from inventory_email_support.views.prepended_body_view import GetPrependedBody, EditPrependedBody
from inventory_email_support.views.subject_tag_view import GetSubjectTag, EditSubjectTag
from inventory_email_support.views.subscribed_manager_view import Subscribe, Unsubscribe, SubscribedManagerList

urlpatterns = [
    url(r'^subscribedManagers/$', SubscribedManagerList.as_view(), name='subscribed-manager-list'),
    url(r'^subscribe/$', Subscribe.as_view(), name='subscribe'),
    url(r'^unsubscribe/$', Unsubscribe.as_view(), name='unsubscribe'),
    url(r'^subjectTag/$', GetSubjectTag.as_view(), name='get-subject-tag'),
    url(r'^subjectTag/edit/$', EditSubjectTag.as_view(), name='edit-subject-tag'),
    url(r'^prependedBody/$', GetPrependedBody.as_view(), name='get-prepended-body'),
    url(r'^prependedBody/edit/$', EditPrependedBody.as_view(), name='edit-prepended-body'),
    url(r'^loanReminderDates/$', GetLoanReminderDates.as_view(), name='loan-reminder-dates'),
    url(r'^loanReminderDates/create/$', CreateLoanReminderDates.as_view(), name='create-loan-reminder-dates'),

]
