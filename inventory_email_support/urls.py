from django.conf.urls import url

from inventory_email_support.views.loan_reminder_email_view import GetLoanReminderDates, ModifyLoanReminderDates
from inventory_email_support.views.prepended_body_view import GetPrependedBody, ModifyPrependedBody
from inventory_email_support.views.subject_tag_view import GetSubjectTag, ModifySubjectTag
from inventory_email_support.views.subscribed_manager_view import Subscribe, Unsubscribe, SubscribedManagerList

urlpatterns = [
    url(r'^subscribedManagers/$', SubscribedManagerList.as_view(), name='subscribed-manager-list'),
    url(r'^subscribe/$', Subscribe.as_view(), name='subscribe'),
    url(r'^unsubscribe/$', Unsubscribe.as_view(), name='unsubscribe'),
    url(r'^subjectTag/$', GetSubjectTag.as_view(), name='get-subject-tag'),
    url(r'^subjectTag/modify/$', ModifySubjectTag.as_view(), name='modify-subject-tag'),
    url(r'^prependedBody/$', GetPrependedBody.as_view(), name='get-prepended-body'),
    url(r'^prependedBody/modify/$', ModifyPrependedBody.as_view(), name='modify-prepended-body'),
    url(r'^loanReminderDates/$', GetLoanReminderDates.as_view(), name='get-loan-reminder-dates'),
    url(r'^loanReminderDates/modify/$', ModifyLoanReminderDates.as_view(), name='modify-loan-reminder-dates'),
]
