from django.contrib.auth.models import User
from django.utils import timezone
from posts.models import AGPost, Comment, Reply
from django.urls import reverse
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from . import user_email_utility
from .encryption_utility import *


def unnotify_confirmation(request):
    if "POST" == request.method:
        raise Http404

    try:
        token = request.GET.get("token", None)

        if not token:
            msg = "Invalid Link"
            return render(request, 'msgpage.html', {'msg': msg})

        token = decrypt(token)
        if token:
            token = token.split("-")
            username, trun_date, type, agpost_ref_num = token

            agpost = AGPost.objects.get(ref_number=agpost_ref_num)
            user = User.objects.get(username=username)

            if type == "comment":
                for comment in Comment.objects.get(author=user, agpost=agpost):
                    if comment.created_on[11:26] == trun_date:
                        target = comment
                        break

            elif type == "reply":
                for reply in Reply.objects.get(author=user, comment__agpost=agpost):
                    if reply.created_on[11:26] == trun_date:
                        target = reply
                        break
            else:
                target = None

            if target:
                target.notify = False
                target.save()
                msg = "Request complete!"
                foot = "Notifcations for your reply have been disabled."
                return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

            msg = "An error occured. Email me at aaahhhghosts@gmail.com and I'll get this sorted out!"
        else:
            msg = "Invalid Link"

    except Exception as e:
        logging.getLogger("error").error("There was an exception while deleting user ", username, e)

    return render(request, 'msgpage.html', {'msg': msg})


# Request deletion of account
def request_deletion(request):
    # If user is logged in and makes post request
    user = request.user
    if user.is_authenticated:

        # Get data from homepage
        email = user.email
        username = user.username

        # Create token and build confirm link
        token = encrypt(email + "-" + str((timezone.now().today().strftime("%Y%m%d"))))
        deletion_confirmation_url = request.build_absolute_uri(
            reverse('users:deletion_confirmation')) + "?token=" + token

        # Send confirmation email and return status
        status = user_email_utility.send_deletion_email(email, username, deletion_confirmation_url)
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

        # Get requesting user's email and username
        email = token[0]

        # Get the number of days since link was created
        link_date = int(token[1])
        today_date = int(timezone.now().today().strftime("%Y%m%d"))
        delta = today_date - link_date

        # If link is 2 or less days old, trust it and delete
        if 0 <= delta <= 2:

            # If user with this email exists, and that user
            # has same username, deactivate the user
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if delete_user(user):
                    msg = "Account deleted. Take care!"
                    return render(request, 'msgpage.html', {'msg': msg})

    # Return error is failed decrypt
    msg = "Link Invalid or Timed Out"
    return render(request, 'msgpage.html', {'msg': msg})


# Function for deactivating users
def delete_user(user):

    email = str(user.email)
    try:
        # Deactivate all comments and replies first
        for comment in User.comments:
            comment.active = False
        for reply in User.replies:
            reply.active = False

        # Deactivate user
        user.is_active = False
        user.save()

    except Exception as e:
        logging.getLogger("error").error("There was an exception while deleting user ", email, e)
        return False

    logging.getLogger("DEBUG").debug("User ", email, " deleted.")
    return True
