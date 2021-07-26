import logging
from users.user_email_utility import send_email
from django.conf import settings
from django.template.loader import get_template
from django.utils.html import strip_tags
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from posts.models import Comment, Reply, AGPostView
from homepage.models import Subscriber


User = get_user_model()


class Command(BaseCommand):
    help = 'Creates and send daily report to scuub'

    def handle(self, *args, **options):

        today = timezone.now().today()
        scuubs_email = settings.EMAIL_HOST_USER

        todays_subs = Subscriber.objects.filter(date_created__date=today)
        todays_users = User.objects.filter(date_joined__date=today)
        todays_comments = Comment.objects.filter(created_on__date=today)
        todays_replies = Reply.objects.filter(created_on__date=today)
        todays_views = AGPostView.objects.filter(created_on__date=today)

        sub_list = ""
        for sub in todays_subs:
            sub_list += (str(sub.email) + '\n')

        user_list = ""
        for user in todays_users:
            user_list += (user.get_full_name() + '\n')

        comment_list = ""
        for comment in todays_comments:
            comment_list += (str(comment) + '\n')

        reply_list = ""
        for reply in todays_replies:
            reply_list += (str(reply) + '\n')

        data = dict()
        data["subs_header"] = str(len(todays_subs)) + " subscribers joined today:\n"
        data["users_header"] = str(len(todays_users)) + " users joined today:\n"
        data["comments_header"] = str(len(todays_comments)) + " comments posted today:\n"
        data["replies_header"] = str(len(todays_replies)) + " replies posted today:\n"
        data["sub_list"] = sub_list
        data["user_list"] = user_list
        data["comment_list"] = comment_list
        data["reply_list"] = reply_list
        data["view_count"] = str(len(todays_views))

        # Render email text (html and plain) and set subject
        template = get_template("email_templates/daily_report.html")
        html_content = template.render(data)
        text_content = strip_tags(html_content)
        subject = today.strftime("%Y-%m-%d") + " Blog Report"
        if not (user_list, comment_list, reply_list):
            subject += " EMPTY"

        was_sent = send_email(scuubs_email, subject, html_content, text_content)

        if was_sent:
            logging.getLogger("DEBUG").debug('Daily report sent')
            self.stdout.write(self.style.SUCCESS('Daily report sent'))
        else:
            raise CommandError('Failed sending report')
