from django.core.mail import send_mail
from smtplib import SMTPException
import logging


def send_email(email, subject, html_content, text_content):

    # Send email with subject as both html and plain text
    try:
        send_mail(subject, text_content, None, [email], html_message=html_content, fail_silently=True)
        return True
    except SMTPException as e:
        logging.getLogger("error").error("There was an SMTPException sending a user email: ", e)
        return False
