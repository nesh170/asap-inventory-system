from django.db import models


class Log(models.Model):
    user = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    timestamp = models.TimeField(auto_now=True)
    log_text = models.TextField()

    def __str__(self):
        log_string = "User {user} logged the following: {log}".format
        return log_string(user=self.user, log=self.log_text)