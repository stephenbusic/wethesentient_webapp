from django.contrib.auth.models import User
from posts.models import AGPost, Comment, Reply
from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login, logout
from .forms import CreatePassword, LoginUser, SendPasswordReset
from . import user_email_utility
from .encryption_utility import *
from datetime import date
from random import randint


def unnotify_comment_confirmation(request):
    if "POST" == request.method:
        raise Http404

    token = request.GET.get("token", None)

    if not token:
        msg = "Invalid Link"
        return render(request, 'msgpage.html', {'msg': msg})

    token = decrypt(token)
    if token:
        token = token.split("-")
        email = token[0]
        trun_date = token[1]
        agpost_title = token[2]
        agpost = AGPost.objects.get(title=agpost_title)

        for comment in agpost.comments.all():
            if str(comment.created_on)[11:26] == trun_date and comment.email == email:
                comment.notify = False
                comment.save()
                msg = "Request complete!"
                foot = "Notifcations for your comment have been disabled."
                return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

        msg = "An error occured. Email me at aaahhhghosts@gmail.com and I'll get this sorted out!"
    else:
        msg = "Invalid Link"

    return render(request, 'msgpage.html', {'msg': msg})


def unnotify_reply_confirmation(request):
    if "POST" == request.method:
        raise Http404

    token = request.GET.get("token", None)

    if not token:
        msg = "Invalid Link"
        return render(request, 'msgpage.html', {'msg': msg})

    token = decrypt(token)
    if token:
        token = token.split("-")
        email = token[0]
        trun_date = token[1]
        agpost_title = token[2]
        agpost = AGPost.objects.get(title=agpost_title)

        for comment in agpost.comments.all():
            for reply in comment.replies.all():
                if str(reply.created_on)[11:26] == trun_date and reply.email == email:
                    reply.notify = False
                    reply.save()
                    msg = "Request complete!"
                    foot = "Notifcations for your reply have been disabled."
                    return render(request, 'msgpage.html', {'msg': msg, 'foot': foot})

        msg = "An error occured. Email me at aaahhhghosts@gmail.com and I'll get this sorted out!"
    else:
        msg = "Invalid Link"

    return render(request, 'msgpage.html', {'msg': msg})


# Utility functions
def save_user(email, username, password):
    # Save user to blog
    if not User.objects.filter(email=email).exists() and \
            not User.objects.filter(username=username).exists():
        new_user = User()
        new_user.email = email
        new_user.username = username
        new_user.set_password(password)
        new_user.date_joined = date.today()
        new_user.save()
        return True
    else:
        return False


# Request deletion of account
def request_deletion(request):

    # If user is logged in and makes post request
    user = request.user
    if user.is_authenticated:

        # Get data from homepage
        email = user.email
        username = user.username

        # Create token and build confirm link
        token = encrypt(email + "-" + username + "-" + str(randint(10, 99)))
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
        username = token[1]

        # If user with this email exists, and that user
        # has same username, deactivate the user
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if user.username == username:
                if delete_user(user):
                    msg = "Account deleted. Take care!"
                    return render(request, 'msgpage.html', {'msg': msg})

    # Return error is failed decrypt
    msg = "Error"
    return render(request, 'msgpage.html', {'msg': msg})


# Function for deactivating users
def delete_user(user):
    username = str(user.username)
    email = str(user.email)
    try:
        # Delete all comments and replies first
        for comment in Comment.objects.filter(email=email):
            for reply in comment.replies.all():
                reply.deactive()
            comment.deactivate()

        for reply in Reply.objects.filter(email=email):
            reply.deactivate()

        # Deactivate user
        user.active = False
        user.delete()
    except Exception as e:
        logging.getLogger("error").error("There was an exception will deleting user ", username)
        return False

    logging.getLogger("DEBUG").debug("User ", username, " deleted.")
    return True
