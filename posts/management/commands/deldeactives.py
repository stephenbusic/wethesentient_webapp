import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from posts.models import Comment, Reply

User = get_user_model()

class Command(BaseCommand):
    help = 'Deletes deactivated users, comments, and replies that ' \
           'have been deactivated for more than three days.'

    def handle(self, *args, **options):

        days_to_live = 5
        now = timezone.now()
        time_threshhold = now - timezone.timedelta(days=days_to_live)
        del_count = 0

        # Delete inactive replies
        for reply in Reply.objects.filter(active=False, deactivated_on__lt=time_threshhold):
            reply.delete()
            del_count += 1

        # Delete inactive comments
        for comment in Comment.objects.filter(active=False, deactivated_on__lt=time_threshhold):
            comment.delete()
            del_count += 1

        # Delete inactive users
        for user in User.objects.filter(is_active=False, last_login__lt=time_threshhold):
            user.delete()
            del_count += 1

        logging.getLogger("DEBUG").debug('RAN DELDEACTIVES: Deleted %s inactive objects' % del_count)

        self.stdout.write(self.style.SUCCESS('Deleted %s inactive objects' % del_count))
