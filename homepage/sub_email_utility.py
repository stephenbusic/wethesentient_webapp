from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from .models import Subscriber
from django.urls import reverse
from urllib.parse import urljoin
from .encryption_utility import encrypt
from common.util.send_email import send_email
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def send_subscription_email(email, sub_confirmation_url):

    # dictionary to store email-related variables
    data = dict()
    data["confirmation_url"] = sub_confirmation_url
    template = get_template("email_templates/sub_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Confirm Subscription"
    return send_email(email, subject, html_content, text_content)


def send_unsub_email(email, username, unsub_confirmation_url):
    data = dict()
    data["email"] = email
    data["first_name"] = username.split(' ')[0]
    data["confirmation_url"] = unsub_confirmation_url
    template = get_template("email_templates/deletion_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Cancel Subscription"
    return send_email(email, subject, html_content, text_content)


def send_subs_new_post_email(agpost):

    for sub in Subscriber.objects.all():

        domain = Site.objects.get_current().domain
        absolute_path = 'https://' + str(format(domain))

        # Build unsubscribe link
        token = encrypt(sub.email + "-" + timezone.now().today().strftime("%Y%m%d"))
        unsub_confirmation = urljoin(absolute_path, reverse('homepage:unsub_confirmation') + "?token=" + token)

        # Build post link
        post_url = urljoin(absolute_path, reverse('posts:show', kwargs={'slug': agpost.slug}))

        data = dict()
        data["desc"] = agpost.desc
        data["body"] = agpost.body
        data["post_url"] = post_url
        data["unsubscribe_url"] = unsub_confirmation
        template = get_template("email_templates/post_email.html")

        # Render email text (html and plain) and set subject
        html_content = template.render(data)
        text_content = strip_tags(html_content)
        subject = agpost.title

        logging.info("Trying to send notification email for post " + subject + " to sub " + sub.email + "...")
        status = send_email(sub.email, subject, html_content, text_content)

        if status:
            logger.info("SUCCESS: Notification sent to sub " + sub.email + " for post " + subject)
        else:
            logger.error("ERROR: Notification FAILED to send to sub " + sub.email + " for post " + subject)
