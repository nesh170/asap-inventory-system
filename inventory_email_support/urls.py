from django.conf.urls import url

from inventory_email_support.views.email_view import Subscribe, Unsubscribe, EditSubjectTag

urlpatterns = [
    url(r'^subscribe/$', Subscribe.as_view(), name='subscribe'),
    url(r'^unsubscribe/$', Unsubscribe.as_view(), name='unsubscribe'),
    url(r'^subjectTag/$', EditSubjectTag.as_view(), name='edit-subject-tag'),

]
