from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from homepage import validation_utility
from homepage import sub_email_utility
from homepage.encryption_utility import *
from homepage.forms import SubscriberForm
from homepage.models import Subscriber
import requests, json


def show_homepage(request):

    # If user is logged in and makes post request
    if request.method == 'POST':

        # If new comment is created
        if 'create_subscription' in request.POST:
            sub_form = SubscriberForm(data=request.POST)

            # If comment form is valid, try and get reCaptcha score
            if sub_form.is_valid():
                try:
                    result = requests.post(
                        'https://www.google.com/recaptcha/api/siteverify',
                        data={
                            'secret': settings.RECAPTCHA_SECRET_KEY,
                            'response': request.POST.get("g-recaptcha-response"),
                        }
                    ).content
                except ConnectionError:  # Handle your error state
                    result = ""

                # Will throw ValueError if we can't parse Google's response
                result = json.loads(result)

                # If recaptcha state is success and score is good, save comment
                if result['success'] and result['score'] >= 0.5:

                    # Get data from homepage
                    post_data = request.POST.copy()
                    email = post_data.get("email", None)

                    # Make sure email is valid
                    error_msg = validation_utility.validate_email(email)
                    if error_msg:
                        return render(request, 'msgpage.html', {'msg': error_msg})

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
                        else:
                            msg = "Sorry. Sending confirmation email failed. Try again later!"
                            foot = ""

                        return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

                    else:
                        msg = "Email is already subscribed!"
                        foot = "If you are trying to unsubscribe, look for a unsubscription link at the bottom of any of my emails."
                        return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

    # If form invalid, return to homepage
    site_key = settings.RECAPTCHA_SITE_KEY
    return render(request, 'index.html', {'site_key': site_key})


def show_policy(request):

    # Display AAAHHHghosts privacy policy
    return render(request, 'policy.html', {})


def sub_confirmation(request):

    # Make sure method is valid
    if "POST" == request.method:
        raise Http404

    # Check if token, return error if not
    token = request.GET.get("token", None)
    if not token:
        msg = "Invalid Link"
        return render(request, 'msgpage.html', {'msg': msg})

    # Extract data from token, if successfully decrypted
    token = decrypt(token)
    if token:
        token = token.split("-")
        sub_email = token[0]

        # Get date the link was created
        link_date = int(token[1])

        # If link has not timed out, trust it and unsub
        if hasnt_timed_out(link_date, 2):

            # If subscriber with email does not already exist, create account
            if not Subscriber.objects.filter(email=sub_email):
                new_sub = Subscriber(email=sub_email)
                new_sub.save()
                msg = "Subscription confirmed. Thank you for following my blog!"
                return render(request, 'msgpage.html', {'msg': msg})

            # If subscriber does already exists, inform user and drop account
            else:
                msg = "Email is already subscribed!"
                foot = "If you are trying to unsubscribe, look for a unsubscription link at the bottom of any of my emails."
                return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

    # Return error is failed decrypt
    msg = "Link Invalid or Timed Out"
    return render(request, 'msgpage.html', {'msg': msg})


def unsub_confirmation(request):
    if "POST" == request.method:
        raise Http404

    token = request.GET.get("token", None)

    if not token:
        logging.getLogger("warning").warning("Invalid Link ")
        msg = "Invalid Link"
        return render(request, 'msgpage.html', {'msg': msg})

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
            return render(request, 'msgpage.html', {'msg': msg})

    msg = "Link Invalid or Timed Out"
    return render(request, 'msgpage.html', {'msg': msg})


# Method to determine if link has timed out
def hasnt_timed_out(link_date, max_age):
    today_date = int(timezone.now().today().strftime("%Y%m%d"))
    delta = today_date - link_date
    return 0 <= delta <= max_age

