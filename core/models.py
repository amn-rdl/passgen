from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    email = models.EmailField(unique=True)
    pp = CloudinaryField(blank=True, null=True)
    def __str__(self):
        return f'Compte de {self.username}'
