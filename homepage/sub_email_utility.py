import asyncio

from django.template.loader import get_template
from django.utils import timezone
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from .models import Subscriber
from django.urls import reverse
from urllib.parse import urljoin
from .encryption_utility import encrypt
from common.util.send_email import send_email
from asgiref.sync import sync_to_async
import logging
from multiprocessing import Process, Lock
import django
import multiprocessing as mp
# mp.set_start_method('fork')
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


# Add a send_email task in the event loop for each subscriber.
async def setup_async_sub_email_loop(agpost, loop):

    # Get absolute path
    domain = await get_domain()
    absolute_path = 'https://' + str(format(domain))

    # Build post link
    post_url = urljoin(absolute_path, reverse('posts:show', kwargs={'slug': agpost.slug}))

    # Make dict for email data
    data = dict()
    data["desc"] = agpost.desc
    data["body"] = agpost.body
    data["post_url"] = post_url
    template = get_template("email_templates/post_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = agpost.title

    # Iterate for each user.
    for i, sub in enumerate(await get_all_subs()):

        # Get this subscriber's email
        email = sub.email

        # Build unique unsubscribe link
        token = encrypt(email + "-" + timezone.now().today().strftime("%Y%m%d"))
        unsub_confirmation = urljoin(absolute_path, reverse('homepage:unsub_confirmation') + "?token=" + token)

        # Add unique unsub url to email data
        data["unsubscribe_url"] = unsub_confirmation

        # Attempt to send notification email
        logging.info("Trying to send notification email for post " + subject + " to sub " + email + "...")
        loop.create_task(try_to_send_post_notification(email, subject, html_content, text_content), name=("task" + str(i)))


# Send notification email, log the results.
async def try_to_send_post_notification(email, subject, html_content, text_content):
    if send_email(email, subject, html_content, text_content):
        logger.info("SUCCESS: Notification sent to sub " + email + " for post " + subject)
    else:
        logger.error(
            "ERROR: Notification FAILED to send to sub " + email + " for post " + subject)


# Entry point for execution.
def send_subs_new_post_email(agpost):
    logger.info("Setting up async emailing loop...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_async_sub_email_loop(agpost, loop))
    loop.close()


@sync_to_async
def get_all_subs():
    return list(Subscriber.objects.all())


@sync_to_async
def get_domain():
    return Site.objects.get_current().domain


