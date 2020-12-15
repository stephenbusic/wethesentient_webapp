from random import randint
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from . import validation_utility
from . import sub_email_utility
from .encryption_utility import *
from .forms import SubscriberForm
from follow.models import Subscriber
import requests, json
from django.conf import settings


def request_sub(request):

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
                if result['success'] == True and result['score'] >= 0.5:

                    # Get data from homepage
                    post_data = request.POST.copy()
                    email = post_data.get("email", None)
                    username = post_data.get("username", None)

                    # Make sure email is valid
                    error_msg = validation_utility.validate_email(email)
                    if error_msg:
                        return render(request, 'msgpage.html', {'msg': error_msg})

                    # Make sure first and last name is valid
                    if not username:
                        msg = "Error: No name provided."
                        return render(request, 'msgpage.html', {'msg': msg})

                    # Check if user already exists for this email or username
                    if not Subscriber.objects.filter(email=email).exists():

                        # Create token and build confirm link
                        token = encrypt(email + "-" + username + "-" + str(randint(10, 99)))
                        subscription_confirmation_url = request.build_absolute_uri(
                            reverse('follow:sub_confirmation')) + "?token=" + token

                        # Send confirmation email and return status
                        status = sub_email_utility.send_subscription_email(email, username, subscription_confirmation_url)
                        if status == "sent":
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

    #If form invalid, return to follow page
    site_key = settings.RECAPTCHA_SITE_KEY
    return render(request, 'follow.html', {'site_key': site_key})


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

        sub_data = dict()
        sub_data["email"] = token[0]
        sub_data["username"] = token[1]

        new_sub = Subscriber(**sub_data)
        new_sub.save()

        msg = "Subscription confirmed. Thank you for following my blog!"
        return render(request, 'msgpage.html', {'msg': msg})
    else:
        # Return error is failed decrypt
        msg = "Invalid Link"
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
        token = token.split("-")
        email = token[0]

        save_status = Subscriber.objects.get(email=email).delete()
        if save_status:
            msg = "Unsubscribed. So long, cap'n <3"
        else:
            msg = "An error occured. Email me at aaahhhghosts@gmail.com and I'll get this sorted out!"
    else:
        msg = "Invalid Link"

    return render(request, 'msgpage.html', {'msg': msg})


def sub_doesnt_exist(email):

    # Check if user already exists for this email
    try:
        sub = Subscriber.objects.get(email=email)
        return False
    except Subscriber.DoesNotExist:
        return True
