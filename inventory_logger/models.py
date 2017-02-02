from django.db import models


class Log(models.Model):
    user = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
    description = models.TextField()

    def __str__(self):
        log_string = "User {user} logged the following: {log}".format
        return log_string(user=self.user, log=self.description)
