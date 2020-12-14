from django.db import models

class Subscriber(models.Model):
    username = models.CharField(max_length=160)
    email = models.CharField(max_length=160)
    date_created = models.DateField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.username
