from django.db import models

from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
