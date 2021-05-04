from django.template.loader import get_template
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.urls import reverse
from urllib.parse import urljoin
from .encryption_utility import encrypt
from django.core.mail import EmailMultiAlternatives
from smtplib import SMTPException
import logging
from django.conf import settings


def send_email(email, subject, html_content, text_content):

    #Send email with subject as both html and plain text
    msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
    msg.attach_alternative(html_content, "text/html")
    try:
        msg.send(fail_silently=False)
    except SMTPException as e:
        logging.getLogger("error").error("There was an SMTPException sending a user email: ", e)
        return "error"
    return "sent"


def send_commenter_reply_notice(reply):

    domain = Site.objects.get_current().domain
    absolute_path = 'https://www.' + str(format(domain))

    parent_comment = reply.comment
    email = parent_comment.email
    trun_date = str(parent_comment.created_on)[11:26]
    agpost = parent_comment.agpost

    # Build unsubscribe link
    token = encrypt(email + "-" + trun_date + "-" + agpost.title)
    unnotify_confirmation_url = urljoin(absolute_path, reverse('users:unnotify_comment_confirmation') + "?token=" + token)

    # Build post link
    post_url = urljoin(absolute_path, reverse('posts:show', kwargs={'slug': agpost.slug}))

    data = dict()
    data["first_name"] = parent_comment.username.split(' ')[0]
    data["replier_name"] = reply.username
    data["agpost_title"] = agpost.title
    data["body"] = reply.body
    data["post_url"] = post_url
    data["unnotify_url"] = unnotify_confirmation_url
    template = get_template("email_templates/reply_notify_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Someone Replied to your Comment"
    return send_email(email, subject, html_content, text_content)


def send_replier_reply_notice(parent_reply, reply):

    domain = Site.objects.get_current().domain
    absolute_path = 'https://www.' + str(format(domain))

    email = parent_reply.email
    print("email: " + str(email))
    trun_date = str(parent_reply.created_on)[11:26]
    agpost = reply.comment.agpost

    # Build unsubscribe link
    token = encrypt(email + "-" + trun_date + "-" + agpost.title)
    unnotify_confirmation_url = urljoin(absolute_path, reverse('users:unnotify_reply_confirmation') + "?token=" + token)

    # Build post link
    post_url = urljoin(absolute_path, reverse('posts:show', kwargs={'slug': agpost.slug}))

    data = dict()
    data["first_name"] = parent_reply.username.split(' ')[0]
    data["replier_name"] = reply.username
    data["agpost_title"] = agpost.title
    data["body"] = reply.body
    data["post_url"] = post_url
    data["unnotify_url"] = unnotify_confirmation_url
    template = get_template("email_templates/reply_notify_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Someone Responded to your Reply"
    return send_email(email, subject, html_content, text_content)


def send_deletion_email(email, username, deletion_confirmation_url):

    #Build dictionary to store email-related variables
    data = dict()
    data["first_name"] = username.split(' ')[0]
    data["deletion_url"] = deletion_confirmation_url
    template = get_template("email_templates/deletion_email.html")

    #Render email text (html and plain) and set subjet
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Confirm Deletion"
    return send_email(email, subject, html_content, text_content)

