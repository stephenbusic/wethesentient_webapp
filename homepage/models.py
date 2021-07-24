from django.db import models


class Subscriber(models.Model):
    email = models.CharField(max_length=160)
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_created']
        verbose_name_plural = "Subscribers"

    def __str__(self):
        return self.email
