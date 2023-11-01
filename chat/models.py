from django.db import models
from users.models import User


# Create your models here.

class Messages(models.Model):
    description = models.TextField()
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', unique=False)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver', unique=False)
    time = models.TimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"To: {self.receiver} From: {self.sender}"

    class Meta:
        ordering = ('timestamp',)


class Friends(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend = models.IntegerField()

    def __str__(self):
        return f"{self.friend}"
