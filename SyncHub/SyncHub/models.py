from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    student_number = models.CharField(
        max_length=7,
        unique=True,
        validators=[RegexValidator(r'^\d{7}$', 'Student number must be exactly 7 digits.')],
        help_text='Enter a unique 7-digit student number.'
    )

    USERNAME_FIELD = 'student_number'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
