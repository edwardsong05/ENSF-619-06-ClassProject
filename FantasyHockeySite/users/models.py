from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # add additional fields in here
    first_name = models.CharField(db_column='First Name', max_length=45, null=False)
    last_name = models.CharField(db_column='Last Name', max_length=45, null=False)
    def __str__(self):
        return self.email