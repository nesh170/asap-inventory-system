from django.db import models


class Action(models.Model):
    color = models.CharField(max_length=9, unique=True)
    tag = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tag


class Log(models.Model):
    user = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
    action = models.ForeignKey(Action, on_delete=models.CASCADE, related_name='logs')
    description = models.TextField()

    def __str__(self):
        log_string = "User {user} logged the following: {log}".format
        return log_string(user=self.user, log=self.description)
