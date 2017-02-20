from django.db import models

# Create your models here.

class Auth(models.Model):
    name = models.CharField(max_length=30)
