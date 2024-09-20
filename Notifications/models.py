from django.db import models
from authentication.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_affiliation = models.BooleanField(default=False)
    amount = models.IntegerField(default=0)
    affiliate = models.CharField(blank=True,null=True)

    def __str__(self):
        return f'Notification for {self.user.email}'
