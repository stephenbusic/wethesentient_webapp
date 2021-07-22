from django.utils import timezone
from posts.models import AGPost, Comment, Reply
from django.urls import reverse
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from . import user_email_utility
from .encryption_utility import *
from django.contrib.auth import get_user_model

User = get_user_model()

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
            username, date_string, type, agpost_ref_num = token

            agpost = AGPost.objects.get(ref_number=agpost_ref_num)
            user = User.objects.get(username=username)

            # Determine whether target is a reply or comment, and hence
            # where to search
            if type == "comment":
                list_to_search = Comment.objects.filter(author=user, agpost=agpost)
            elif type == "reply":
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
                    foot = "Notifcations for your reply have been disabled."
                    return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

    except Exception as e:
        logging.getLogger("error").error("There was an exception while trying to disable notifications for " +
                                         username + '\'s ' + type + ": " + str(e))

    return render(request, 'msgpage.html', {'msg': "Invalid Link"})


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
        for comment in user.comments.all():
            comment.active = False
            comment.save()

        for reply in user.replies.all():
            reply.active = False
            reply.save()

        # Deactivate user
        user.is_active = False
        user.save()

    except Exception as e:
        logging.getLogger("error").error("There was an exception while deactivating user " +
                                         str(user.email) + ": " + str(e))
        return False

    logging.getLogger("DEBUG").debug("User " + str(user.email) + " deactivated.")
    return True
