from django.db import models

from django.db import models

class Officer(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    rfid_tag = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class TimeLog(models.Model):
    officer = models.ForeignKey(Officer, on_delete=models.CASCADE)
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.officer.name} - {self.date}"
