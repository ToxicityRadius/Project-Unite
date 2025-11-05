from django.db import models
from django.core.validators import RegexValidator

class Officer(models.Model):
    id = models.CharField(
        max_length=7,
        primary_key=True,
        validators=[RegexValidator(r'^\d{7}$', 'ID must be exactly 7 digits.')],
        help_text='Enter a unique 7-digit ID.'
    )
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class TimeLog(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField()

    def __str__(self):
        return f"{self.officer.name} - {self.date}"
