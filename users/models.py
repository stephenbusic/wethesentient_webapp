from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
import logging

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:

        # Add the default permission to create comments/replies
        try:
            can_speak_perm = Permission.objects.get(codename='can_comment_or_reply')
            instance.user_permissions.add(can_speak_perm)

        except Permission.DoesNotExist:
            logger = logging.getLogger('__users__')
            logger.error("User was created without default permission to "
                         + "create comments or replies.")
