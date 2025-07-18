from django.db.models import Count
from django.db.models.functions import TruncDay
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from .validation_utility import validateEmail
from common.util.recaptcha_utility import pass_recaptcha
from . import sub_email_utility
from .encryption_utility import encrypt, decrypt
from .forms import SubscriberForm
from .models import Subscriber
import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)


# Show index page
def show_homepage(request):
    # If user is logged in and makes post request
    if request.method == 'POST' and pass_recaptcha(request):

        # If new subscription is created
        if 'create_subscription' in request.POST:
            return process_sub_form(request)

    # If form invalid, return to homepage
    site_key = settings.RECAPTCHA_SITE_KEY
    return render(request, 'index.html', {'site_key': site_key})


# Function for processing sub form. Separate so that
# it can be used on the agpost page too.
def process_sub_form(request):
    sub_form = SubscriberForm(data=request.POST)

    # If comment form is valid, try and get reCaptcha score
    if sub_form.is_valid():

        # Get data from homepage
        post_data = request.POST.copy()
        email = post_data.get("email", None)

        # Make sure email is valid
        if not validateEmail(email):
            return render(request, 'msgpage.html', {'msg': "email is invalid"})

        # Check if user already exists for this email or username
        if not Subscriber.objects.filter(email=email):

            # Create token and build confirm link
            token = encrypt(email + "-" + timezone.now().today().strftime("%Y%m%d"))
            subscription_confirmation_url = request.build_absolute_uri(
                reverse('homepage:sub_confirmation')) + "?token=" + token

            # Send confirmation email and return status
            if sub_email_utility.send_subscription_email(email, subscription_confirmation_url):
                msg = "Thanks for subscribing. Check inbox to confirm <3"
                foot = "Might be in your junk folder btw."
                logger.info("SUCCESS: sub email sent to " + email)
            else:
                msg = "Sorry. Sending confirmation email failed. Try again later!"
                foot = ""
                logger.error("ERROR: FAILED to send to sub email to " + email)
            return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

        else:
            msg = "Email is already subscribed!"
            foot = "If you are trying to unsubscribe, look for a unsubscription link at the bottom of any of my emails."
            return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})


def show_policy(request):
    # Display AAAHHHghosts privacy policy
    return render(request, 'policy.html', {})


def show_terms(request):
    # Display AAAHHHghosts privacy policy
    return render(request, 'terms.html', {})


def sub_confirmation(request):

    # If the confirm link has been clicked (either by user or bot),
    # try to get the token and load it into a bot-proof form
    if request.method == 'GET':
        # Check if token. If not, continue to end
        # of function and return invalid link page
        token = request.GET.get("token", None)
        if token:
            # Pass token into a recaptcha bot-proof form
            msg = "Confirm Subscription"
            site_key = settings.RECAPTCHA_SITE_KEY
            return render(request, 'tokenpage.html', {'msg': msg, 'email_token': token, 'site_key': site_key})

    # If the form has been submitted, try to confirm subscription
    if request.method == 'POST' and pass_recaptcha(request):

        # Get token again from post request
        token = request.POST.get('email_token_value', None)

        # Extract data from token, if successfully decrypted
        token = decrypt(token)
        if token:
            token = token.split("-")
            sub_email = token[0]

            # Get date the link was created
            link_date = int(token[1])

            # If link has not timed out, trust it and unsub
            if hasnt_timed_out(link_date, 2) and validateEmail(sub_email):

                # If subscriber with email does not already exist, create sub
                if not Subscriber.objects.filter(email=sub_email):
                    new_sub = Subscriber(email=sub_email)
                    new_sub.save()
                    msg = "Subscription confirmed. Thank you for following my blog!"
                    logger.info("SUCCESS: sub confirmed for " + sub_email)
                    return render(request, 'msgpage.html', {'msg': msg})
                else:
                    msg = "Email is already subscribed!"
                    foot = "If you are trying to unsubscribe, look for a unsubscription link at the bottom of any of " \
                           "my emails. "
                    logger.error("ERROR: FAILED to confirm sub " + sub_email)
                    return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

    # Return error is failed decrypt
    msg = "Link Invalid or Timed Out"
    return render(request, 'msgpage.html', {'msg': msg})


def unsub_confirmation(request):

    # If the confirm link has been clicked (either by user or bot),
    # try to get the token and load it into a bot-proof form
    if request.method == 'GET':
        # Check if token. If not, continue to end
        # of function and return invalid link page
        token = request.GET.get("token", None)
        if token:
            # Pass token into a recaptcha bot-proof form
            msg = "Confirm that you are unsubscribing"
            site_key = settings.RECAPTCHA_SITE_KEY
            return render(request, 'tokenpage.html', {'msg': msg, 'email_token': token, 'site_key': site_key})

    # If the form has been submitted, try to confirm subscription
    if request.method == 'POST' and pass_recaptcha(request):

        # Get token again from post request
        token = request.POST.get('email_token_value', None)

        # Extract data from token, if successfully decrypted
        token = decrypt(token)
        if token:

            # Extract data from unsub link token
            token = token.split("-")
            email = token[0]

            # Get date the link was created
            link_date = int(token[1])

            # If link has not timed out, trust it and unsub
            if hasnt_timed_out(link_date, 7):
                sub = Subscriber.objects.get(email=email)
                sub.delete()
                msg = "Unsubscribed. So long, cap'n <3"
                logger.info("SUCCESS: unsub confirmed for " + email)
                return render(request, 'msgpage.html', {'msg': msg})

    msg = "Link Invalid or Timed Out"
    logger.error("ERROR: FAILED to unsub" + email)
    return render(request, 'msgpage.html', {'msg': msg})


# Method to determine if link has timed out
def hasnt_timed_out(link_date, max_age):
    today_date = int(timezone.now().today().strftime("%Y%m%d"))
    delta = today_date - link_date
    return 0 <= delta <= max_age


# View called by ajax to fetch sub data
def get_subchart_data(request):

    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax and request.method == 'GET':

        duration = 90
        now = timezone.now()
        time_threshhold = now - timezone.timedelta(days=duration)

        # Aggregate new subscribers for the last x number of days
        subs = (
            Subscriber.objects.filter(date_created__gt=time_threshhold)
                .annotate(date=TruncDay("date_created"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )
        total_subs = len(Subscriber.objects.all())
        return JsonResponse({'chart_data': list(subs),
                             'total_subs': total_subs})

    error_msg = "Sorry! Post not found :("
    return render(request, 'msgpage.html', {'msg': error_msg})
