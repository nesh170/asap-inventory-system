from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from post_office.models import Email

class SubscribedManagers(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribed_managers')

    def __str__(self):
        member_string = "Member : {username}".format
        return member_string(username=self.member.username)


class SubjectTag(models.Model):
    subject_tag = models.TextField(null=True, blank=True)

    def __str__(self):
        subject_tag_string = "Subject Tag : {tag}".format
        return subject_tag_string(tag=self.subject_tag)


class PrependedBody(models.Model):
    prepended_body = models.TextField(null=True, blank=True)

    def __str__(self):
        prepended_body_string = "Prepended Body : {tag}".format
        return prepended_body_string(tag=self.prepended_body)

class LoanReminderSchedule(models.Model):
    date = models.DateField()
    executed = models.BooleanField(default=False)

