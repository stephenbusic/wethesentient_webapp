from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created and Group.objects.filter(name='Default').exists():
        instance.groups.add(Group.objects.get(name='Default'))