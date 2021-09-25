from django.template.loader import get_template
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.urls import reverse
from urllib.parse import urljoin
from posts.models import Comment, Reply
from common.util.encryption_utility import encrypt
from common.util.send_email import send_email


def send_reply_notice(parent, reply):

    domain = Site.objects.get_current().domain
    absolute_path = 'https://www.' + str(format(domain))

    recipient = parent.author
    email = recipient.email
    date_string = str(parent.created_on.strftime('%Y%m%d%H%M%S'))

    if isinstance(parent, Comment):
        agpost = parent.agpost
        obj_type = "comment"
    elif isinstance(parent, Reply):
        agpost = parent.comment.agpost
        obj_type = "reply"
    else:
        return False

    # Build unsubscribe link
    token = encrypt(email + "-" + date_string + "-" + obj_type + "-" + str(agpost.pk))
    unnotify_confirmation_url = urljoin(absolute_path, reverse('users:unnotify_confirmation') + "?token=" + token)

    # Build post link
    post_url = urljoin(absolute_path, reverse('posts:show', kwargs={'slug': agpost.slug}))

    data = dict()
    data["first_name"] = recipient.get_full_name()
    data["replier_name"] = reply.author.get_full_name()
    data["agpost_title"] = agpost.title
    data["parent_body"] = parent.body
    data["reply_body"] = reply.body
    data["post_url"] = post_url
    data["unnotify_url"] = unnotify_confirmation_url
    template = get_template("email_templates/reply_notify_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Someone replied to you!"
    return send_email(email, subject, html_content, text_content)


def send_deletion_email(email, deletion_confirmation_url):

    # Build dictionary to store email-related variables
    data = dict()
    data["deletion_url"] = deletion_confirmation_url
    template = get_template("email_templates/deletion_email.html")

    # Render email text (html and plain) and set subject
    html_content = template.render(data)
    text_content = strip_tags(html_content)
    subject = "Confirm Deletion"
    return send_email(email, subject, html_content, text_content)

