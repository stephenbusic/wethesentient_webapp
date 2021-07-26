from django.utils import timezone
from posts.models import AGPost, Comment, Reply
from django.urls import reverse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import user_email_utility
from common.util.recaptcha_utility import pass_recaptcha
from .encryption_utility import *
from django.contrib.auth import get_user_model
import logging

User = get_user_model()


# Confirm the disabling of notifications for some a given comment/reply
def unnotify_confirmation(request):

    # If the confirm link has been clicked (either by user or bot),
    # try to get the token and load it into a bot-proof form
    if request.method == 'GET':
        # Check if token. If not, continue to end
        # of function and return invalid link page
        token = request.GET.get("token", None)
        if token:
            # Pass token into a recaptcha bot-proof form
            msg = "Confirm disabling notifications for your comment"
            site_key = settings.RECAPTCHA_SITE_KEY
            return render(request, 'tokenpage.html', {'msg': msg, 'email_token': token, 'site_key': site_key})

    # If the form has been submitted, try to confirm subscription
    if request.method == 'POST' and pass_recaptcha(request):
        # Get token again from post request
        token = request.POST.get('email_token_value', None)

        token = decrypt(token)
        if token:
            try:
                token = token.split("-")
                email, date_string, obj_type, agpost_pk = token

                agpost = AGPost.objects.get(pk=agpost_pk)
                user = User.objects.get(email=email)

                # Determine whether target is a reply or comment, and hence
                # where to search
                if obj_type == "comment":
                    list_to_search = Comment.objects.filter(author=user, agpost=agpost)
                elif obj_type == "reply":
                    list_to_search = Reply.objects.filter(author=user, comment__agpost=agpost)
                else:
                    return render(request, 'msgpage.html', {'msg': "Invalid Link"})

                # Begin searching for target
                for response in list_to_search:
                    this_date_string = str(response.created_on.strftime('%Y%m%d%H%M%S'))

                    # If date_string match found, conclude this is the target
                    if this_date_string == date_string:
                        target = response
                        target.notify = False
                        target.save()
                        msg = "Request complete!"
                        foot = "Notifcations for your " + obj_type + " have been disabled."
                        return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

            except Exception as e:
                logging.getLogger("error").error("There was an exception while trying to disable notifications. "
                                                 "request: " + str(request) + ' ---ERROR:  ' + str(e))

    return render(request, 'msgpage.html', {'msg': "Invalid Link"})


# Request deletion of account
def request_deletion(request):

    user = request.user
    if user.is_authenticated:

        # Get user email
        email = user.email

        # Create token and build confirm link
        token = encrypt(email + "-" + str((timezone.now().today().strftime("%Y%m%d"))))
        deletion_confirmation_url = request.build_absolute_uri(
            reverse('users:deletion_confirmation')) + "?token=" + token

        # Send confirmation email and return status
        status = user_email_utility.send_deletion_email(email, deletion_confirmation_url)
        if status == "sent":
            msg = "Account deletion email sent. Check inbox to confirm."
            foot = "Be sure to check your junk folder."
        else:
            msg = "Sorry. Sending confirmation email failed. Try again later!"
            foot = ""
        return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

    # If form invalid, return to logout page
    return HttpResponseRedirect(reverse('account_logout'))


# Confirm deletion of account
def deletion_confirmation(request):
    # If the confirm link has been clicked (either by user or bot),
    # try to get the token and load it into a bot-proof form
    if request.method == 'GET':
        # Check if token. If not, continue to end
        # of function and return invalid link page
        token = request.GET.get("token", None)
        if token:
            # Pass token into a recaptcha bot-proof form
            msg = "Confirm account deactivation"
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

            # Get requesting user's email and username
            email = token[0]

            # Get the number of days since link was created
            link_date = int(token[1])

            # If link is 2 or less days old, trust it and delete
            if hasnt_timed_out(link_date, 2):

                # If user with this email exists, and that user
                # has same username, deactivate the user
                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email)
                    # Deactivate user
                    user.is_active = False
                    user.save()

                    logging.getLogger("DEBUG").debug("User " + str(user.email) + " deactivated.")

                    msg = "Account deactivated."
                    foot = "Your account will be permanently deleted after 5 days if you do not login again. Take care!"
                    return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

    # Return error is failed decrypt
    msg = "Link Invalid or Timed Out"
    return render(request, 'msgpage.html', {'msg': msg})


# Method to determine if link has timed out
def hasnt_timed_out(link_date, max_age):
    today_date = int(timezone.now().today().strftime("%Y%m%d"))
    delta = today_date - link_date
    return 0 <= delta <= max_age
