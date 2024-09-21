from django.db import models
from authentication.models import User

# Create your models here.
class Publications(models.Model):


    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    content = models.TextField()
    image_url = models.TextField()
    publication_type = models.CharField()
    date_published = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)