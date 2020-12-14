from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import AGPost
from .forms import CommentForm, ReplyForm
from users.user_email_utility import *
from posts.models import AGPost
from django.conf import settings
import requests, json


def allposts(request):
    all_agposts = AGPost.objects.order_by('-date')
    return render(request, 'allposts.html', { 'all_agposts': all_agposts })


def show_post(request, slug):

    try:
        req_agpost = AGPost.objects.get(slug=slug)
    except:
        req_agpost = None

    if req_agpost is None:
        error_msg = "Sorry! Post not found :("
        return render(request, 'msgpage.html', {'msg': error_msg})
    else:

        active_comments = req_agpost.comments.filter(active=True).order_by('-created_on')
        user = request.user
        site_key = settings.RECAPTCHA_SITE_KEY

        # If user is logged in and makes post request
        if request.method == 'POST' and user.is_authenticated:

            # If new comment is created
            if 'create_comment' in request.POST and user.has_perm('posts.add_comment'):
                comment_form = CommentForm(data=request.POST)

                # If comment form is valid, try and get reCaptcha score
                if comment_form.is_valid():
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

                        # Create comment object but don't save to database yet
                        new_comment = comment_form.save(commit=False)

                        # Assign the current post to the comment
                        new_comment.agpost = req_agpost
                        new_comment.name = user.username
                        new_comment.email = user.email

                        # Save the comment to the database
                        new_comment.save()

                    return HttpResponseRedirect(reverse('posts:show', kwargs={'slug': slug}) + '#comments')
            else:

                # If new reply is created
                if 'create_reply' in request.POST and user.has_perm('posts.add_reply'):

                    # Now knowing a reply form has been submitted (otherwise, how would there
                    # have been a matching key?), get the data from the submitted reply form
                    reply_form = ReplyForm(data=request.POST)
                    if reply_form.is_valid():

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

                        # If recaptcha state is success and score is good, save reply
                        if result['success'] == True and result['score'] >= 0.5:

                            # Figure out which comment was replied to on agpost
                            id_arr = request.POST.get("create_reply").split("_")
                            comment_num = int(id_arr[0])
                            parent_comment = active_comments[comment_num]

                            # Create reply object but don't save to database yet
                            new_reply = reply_form.save(commit=False)

                            # Assign the current post to the comment
                            new_reply.comment = parent_comment
                            new_reply.name = user.username
                            new_reply.email = user.email

                            # Get the reply being replied to.
                            # Also, add handle, if this is a reply to a reply
                            reply_num = int(id_arr[1])
                            if reply_num > 0:
                                active_replies = parent_comment.replies.filter(active=True)
                                parent_reply = active_replies[reply_num - 1]
                                new_reply.handle = "@" + parent_reply.name

                            # Save the comment to the database
                            new_reply.save()

                            # Check if replier is author of original comment
                            # Also check if author of original should be notified
                            isntAuthor = (parent_comment.name != new_reply.name)

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

                                isntAuthor = (parent_reply.name != new_reply.name)
                                if parent_reply.notify and isntAuthor:
                                    send_replier_reply_notice(new_reply, parent_reply)

                        return HttpResponseRedirect(reverse('posts:show', kwargs={'slug': slug}) + '#comments')

        comment_form = CommentForm()
        reply_form = ReplyForm()
        active_comments = req_agpost.comments.filter(active=True)

        return render(request, 'agpost.html', {'agpost': req_agpost, 'comments': active_comments,
                                               'comment_form': comment_form, 'reply_form': reply_form,
                                               'site_key': site_key})