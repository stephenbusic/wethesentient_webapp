from django.contrib.auth.models import User
from posts.models import AGPost
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
    if user_doesnt_exist(email, username):
        new_user = User()
        new_user.email = email
        new_user.username = username
        new_user.set_password(password)
        new_user.date_joined = date.today()
        new_user.save()
        return True
    else:
        return False


def user_doesnt_exist(email, username):

    # Check if user already exists for this email
    try:
        user = User.objects.get(email=email)
        return False
    except User.DoesNotExist:
        pass

    # Check if user already exists for this username
    try:
        user = User.objects.get(username=username)
        return False
    except User.DoesNotExist:
        pass

    # Return false if neither check is true
    return True


# Managing Users

def login_user(request):

    # Create new log in form
    form = LoginUser(request.POST or None)
    if form.is_valid():

        # If form was submitted with no errors, get password
        password = form.clean_password()
        if password:

            # If password checked out, get email and its user
            email = form.clean_email()
            user = User.objects.get(email=email)
            if user:

                # If user was retrieved successfully, log in
                # user and then redirect them back to the post
                login(request, user)
                slug = request.POST.get('slug')
                if slug:
                    return HttpResponseRedirect(reverse('posts:show', kwargs={'slug': slug}))
                else:
                    return HttpResponseRedirect(reverse('posts:show_all_posts'))

    return render(request, 'login.html', {'form': form})


def logout_user(request):

    # If user is actually logged in, get user and log them out
    logged_in = request.user.is_authenticated
    if logged_in:
        logout(request)
        return HttpResponseRedirect(reverse('posts:show_all_posts'))
    else:
        msg = "You are not logged in."
        return render(request, 'msgpage.html', {'msg': msg})