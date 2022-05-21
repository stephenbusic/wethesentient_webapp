from django.core.mail import send_mail
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


def send_email(email, subject, html_content, text_content):

    # Send email with subject as both html and plain text
    logging.info("Sending email to {0}...".format(email))
    sent = bool(send_mail(subject, text_content, None, [email], html_message=html_content, fail_silently=False))
    if sent:
        logging.info("[SUCCESS] email sent!")
    else:
        logging.info("[FAILED] not sent!")
    return sent
