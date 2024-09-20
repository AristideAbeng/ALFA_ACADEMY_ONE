# affiliates/models.py
from django.db import models
from authentication.models import User

class Affiliate(models.Model):
    

    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Links to Django's built-in User model
    referrer = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    direct_points = models.IntegerField(default=0)  # To store the points earned by the affiliate
    indirect_points = models.IntegerField(default=0)  # To store the points earned by the affiliate
    withdrawed_points = models.IntegerField(default=0) #
 

    def __str__(self):
        return self.user.username
