from django.db import models

class Event(models.Model):
    event_id = models.CharField(max_length=255, unique=True)  # Ensure event_id is unique
    created_at = models.DateTimeField(auto_now_add=True)
