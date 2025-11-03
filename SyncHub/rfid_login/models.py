from django.db import models
from django.core.validators import RegexValidator

class Officer(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    rfid_tag = models.CharField(max_length=50, unique=True)
    student_number = models.CharField(
        max_length=7,
        unique=True,
        validators=[RegexValidator(r'^\d{7}$', 'Student number must be exactly 7 digits.')],
        help_text='Enter a unique 7-digit student number.',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.name

class TimeLog(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.officer.name} - {self.date}"
