from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
# Create your models here.


class CustomUserManager(BaseUserManager):

    def create_user(self,email,password=None,**extra_fields):

        extra_fields.setdefault("is_active",True)
        
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self,email,password=None,**extra_fields):

        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault("is_active",True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must be staff"))

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must be superuser"))

        if extra_fields.get("is_active") is not True:
            raise ValueError(_("Superuser must be active"))

        return self.create_user(email,password,**extra_fields)

class User(AbstractUser):

    GENDER_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
    ]
    
    # Fields for storing the user data
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    profession = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True)
    phone1 = models.CharField(max_length=15)
    phone2 = models.CharField(max_length=15, null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # Password stored securely
    is_staff = models.BooleanField(blank=True, null=True)
    is_superuser = models.BooleanField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=False)
    last_login = models.DateTimeField(auto_now=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, null=True)
    account_verification=models.TextField(blank=True,null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name']

    class Meta:
        managed = True
        db_table = 'utilisateur'
    
    objects = CustomUserManager()

    def __str__(self):
        return f'{self.email}'