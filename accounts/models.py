from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
# Create your models here.
GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )

class UserDetail(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: '03000420271'. Up to 13 digits allowed.")
    phone_number = models.BigIntegerField(validators=[phone_regex])  # validators should be a list
    letters_only = RegexValidator(r'^[a-zA-Z ]*$', ('Only letters are allowed.'))
    fullname = models.CharField(max_length=200,validators=[letters_only])
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return self.user.username