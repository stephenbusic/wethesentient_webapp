from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from .models import AGPost
from .forms import CommentForm, ReplyForm
from users.user_email_utility import *
from posts.models import AGPost
from django.conf import settings
import requests, json


def allposts(request, page_num):

    active_agposts = AGPost.objects.filter(active=True).order_by('-date')
    paginator = Paginator(active_agposts, 4)  # Show 4 posts per page.
    page_obj = paginator.get_page(page_num)

    return render(request, 'allposts.html', {'active_agposts': page_obj, })


def show_post(request, slug):

    req_agpost = find_agpost(slug)

    if req_agpost is None:
        error_msg = "Sorry! Post not found :("
        return render(request, 'msgpage.html', {'msg': error_msg})
    else:

        # Get all active comments and current user
        active_comments = req_agpost.comments.filter(active=True).order_by('-created_on')
        user = request.user

        # Proceed to check for a new comment/reply/edit
        # if and only if three conditions are met:
        # 1) User is logged in
        # 2) request is of method POST
        # 3) request passes recaptcha test
        if user.is_authenticated and request.method == 'POST' and pass_recaptcha(request):

            # CREATE NEW COMMENT
            if 'create_comment' in request.POST and user.has_perm('posts.add_comment'):
                comment_form = CommentForm(data=request.POST)

                # If comment form is valid, try and get reCaptcha score
                if comment_form.is_valid():

                    # Create comment object but don't save to database yet
                    new_comment = comment_form.save(commit=False)

                    # Assign the current post to the comment
                    new_comment.agpost = req_agpost
                    new_comment.username = user.username
                    new_comment.email = user.email

                    # Save the comment to the database
                    new_comment.save()

            # CREATE NEW REPLY
            elif 'create_reply' in request.POST and user.has_perm('posts.add_reply'):

                # Now knowing a reply form has been submitted (otherwise, how would there
                # have been a matching key?), get the data from the submitted reply form
                reply_form = ReplyForm(data=request.POST)
                if reply_form.is_valid():

                    # Figure out which comment was replied to on agpost
                    id_arr = request.POST.get("create_reply").split("_")
                    comment_num = int(id_arr[0])
                    parent_comment = active_comments[comment_num]

                    # Create reply object but don't save to database yet
                    new_reply = reply_form.save(commit=False)

                    # Assign the current post to the comment
                    new_reply.comment = parent_comment
                    new_reply.username = user.username
                    new_reply.email = user.email

                    # Also, add handle, if this is a reply to a reply
                    reply_num = int(id_arr[1])
                    if reply_num > 0:
                        active_replies = parent_comment.replies.filter(active=True)
                        parent_reply = active_replies[reply_num - 1]
                        new_reply.handle = "@" + parent_reply.username

                    # Save the comment to the database
                    new_reply.save()

                    # Check if replier is author of original comment
                    # Also check if author of original should be notified
                    isntAuthor = (parent_comment.username != new_reply.username)

                    # Let original commenter know if their comment has been replied to
                    # if commenter set notifications and reply is not posted by them
                    if parent_comment.notify and isntAuthor:
                        send_commenter_reply_notice(new_reply)
                        alreadyNotified = True
                    else:
                        alreadyNotified = False

                    # If reply of reply, AND if author of parent reply is not also
                    # the author of parent comment, notify author of reply
                    if reply_num > 0 and not alreadyNotified:

                        isntAuthor = (parent_reply.username != new_reply.username)
                        if parent_reply.notify and isntAuthor:
                            send_replier_reply_notice(new_reply, parent_reply)

            # EDIT COMMENT
            elif 'edit_comment' in request.POST:

                # Since edits take place via the same form as a reply form, get reply form.
                reply_form = ReplyForm(data=request.POST)
                if reply_form.is_valid():

                    # Figure out which comment was edited
                    id_arr = request.POST.get("edit_comment").split("_")
                    comment_num = int(id_arr[0])
                    parent_comment = active_comments[comment_num]

                    # Proceed only if current logging in user's name and email
                    # matches the author's of the comment the user is trying to edit.
                    # In other words, make sure if user is editing their own comment.
                    if user.username == parent_comment.username and user.email == parent_comment.email:

                        # Create reply object but don't save to database
                        edit = reply_form.save(commit=False)

                        # Update parent comment to have the body of the edit
                        parent_comment.body = edit.body
                        parent_comment.edited = True
                        parent_comment.save()

            # EDIT REPLY
            elif 'edit_reply' in request.POST:

                # Since edits take place via the same form as a reply form, get reply form.
                reply_form = ReplyForm(data=request.POST)
                if reply_form.is_valid():

                    # Figure out which comment the edited reply belongs to
                    id_arr = request.POST.get("edit_reply").split("_")
                    comment_num = int(id_arr[0])
                    parent_comment = active_comments[comment_num]

                    # Find edited reply
                    reply_num = int(id_arr[1])
                    if reply_num > 0:
                        active_replies = parent_comment.replies.filter(active=True)
                        parent_reply = active_replies[reply_num - 1]

                    # Proceed only if current logging in user's name and email
                    # matches the author's of the reply the user is trying to edit.
                    # In other words, make sure if user is editing their own reply.
                    if user.username == parent_reply.username and user.email == parent_reply.email:

                        # Create reply object but don't save to database
                        edit = reply_form.save(commit=False)

                        # Update parent reply to have the body of the edit
                        parent_reply.body = edit.body
                        parent_reply.edited = True
                        parent_reply.save()

            # Reload page at the comment section
            return HttpResponseRedirect(reverse('posts:show', kwargs={'slug': slug}) + '#comments')

        # Define other parameters
        comment_form = CommentForm()
        site_key = settings.RECAPTCHA_SITE_KEY

        return render(request, 'agpost.html', {'agpost': req_agpost, 'comments': active_comments,
                                               'comment_form': comment_form, 'site_key': site_key})


# Function to try and find an existing agpost based on a given slug
def find_agpost(slug):
    try:
        return AGPost.objects.get(slug=slug)
    except AGPost.DoesNotExist:
        return None


# Function to check if a given request passes recaptcha
def pass_recaptcha(request):

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

    # If recaptcha state is success and score is good, return true.
    # Else, return false.
    return result['success'] == True and result['score'] >= 0.5
