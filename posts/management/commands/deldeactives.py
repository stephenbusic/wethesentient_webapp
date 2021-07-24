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

        now = timezone.now()
        days_to_live = 5
        del_count = 0

        # Delete inactive replies
        for reply in Reply.objects.filter(active=False):
            time_since_deactived = now - reply.deactivated_on
            if time_since_deactived.days > days_to_live:
                reply.delete()
                del_count += 1

        # Delete inactive comments
        for comment in Comment.objects.filter(active=False):
            time_since_deactived = now - comment.deactivated_on
            if time_since_deactived.days > days_to_live:
                comment.delete()
                del_count += 1

        # Delete inactive users
        for user in User.objects.filter(is_active=False):
            time_since_last_login = now - user.last_login
            if time_since_last_login.days > days_to_live:
                user.delete()
                del_count += 1

        logging.getLogger("DEBUG").debug('RAN DELDEACTIVES: Deleted %s inactive objects' % del_count)

        self.stdout.write(self.style.SUCCESS('Deleted %s inactive objects' % del_count))
