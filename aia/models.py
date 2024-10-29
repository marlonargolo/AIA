from django.db import models

class Message(models.Model):
    sender = models.CharField(max_length=20)
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(max_length=10)  # 'sent' or 'received'

    def __str__(self):
        return f"{self.sender}: {self.body} ({self.direction})"

