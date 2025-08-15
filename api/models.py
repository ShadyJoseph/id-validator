from django.db import models


class ApiKey(models.Model):
    key = models.CharField(max_length=100, unique=True)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.key

    class Meta:
        app_label = 'api'


class Log(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    national_id = models.CharField(max_length=14)
    valid = models.BooleanField()
    extracted_data = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    api_key_used = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Log for {self.national_id} at {self.timestamp}"

    class Meta:
        app_label = 'api'
