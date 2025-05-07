from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    pp = models.ImageField(upload_to="prof_pics/", blank=True, null=True)
    def __str__(self):
        return f'Compte de {self.username}'
