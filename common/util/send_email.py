from django.core.mail import send_mail
from smtplib import SMTPException, SMTPAuthenticationError
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def send_email(email, subject, html_content, text_content):

    # Send email with subject as both html and plain text
    return bool(send_mail(subject, text_content, None, [email], html_message=html_content, fail_silently=False))
