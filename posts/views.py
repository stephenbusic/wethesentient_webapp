import json
import requests
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from posts.models import AGPost, Reply
from django.db.models import Prefetch
from users.user_email_utility import send_reply_notice
from .forms import CommentForm, DropdownForm
from .models import AGPost


# View to display all existing agposts
def allposts(request, page_num):

    # Get all active agposts
    active_agposts = AGPost.objects.filter(active=True).order_by('-date')

    # Create paginator to show 4 posts per page
    paginator = Paginator(active_agposts, 4)
    page_obj = paginator.get_page(page_num)

    # Render all agposts page
    return render(request, 'allposts.html', {'active_agposts': page_obj, })


# View to show a given agpost
def show_post(request, slug):
    req_agpost = find_agpost(slug)

    if req_agpost is None:
        error_msg = "Sorry! Post not found :("
        return render(request, 'msgpage.html', {'msg': error_msg})
    else:

        # Get all active comments, and for each active
        # comment, get all active replies
        active_comments = req_agpost.comments.filter(active=True)\
            .order_by('rank', '-created_on').prefetch_related(
            Prefetch(
                'replies',
                queryset=Reply.objects.filter(active=True),
                to_attr='active_replies'
            )
        )

        # Get current user
        user = request.user

        # Proceed to check for a new comment/reply/edit
        # if and only if 4 conditions are met:
        # 1) user is logged in
        # 2) user has permission to comment/reply/edit
        # 3) request is of method POST
        # 4) request passes recaptcha test
        if user.is_authenticated and user.has_perm('posts.can_comment_or_reply') and \
                request.method == 'POST' and pass_recaptcha(request):

            # CREATE NEW COMMENT
            if 'is_comment_form' in request.POST:
                comment_form = CommentForm(data=request.POST)

                # If comment form is valid, try and get reCaptcha score
                if comment_form.is_valid():
                    
                    # Create comment object but don't save to database yet
                    new_comment = comment_form.save(commit=False)

                    # Assign the current post to the comment
                    new_comment.agpost = req_agpost
                    new_comment.author = user

                    # Save the comment to the database
                    new_comment.save()

            elif 'is_dropdown_form' in request.POST:

                # Now knowing a reply form has been submitted (otherwise, how would there
                # have been a matching key?), get the data from the submitted reply form
                dropdown_form = DropdownForm(data=request.POST)
                if dropdown_form.is_valid():

                    # Figure out which comment/reply the dropdown form belongs to
                    id = request.POST.get('is_dropdown_form')
                    comment_num, reply_num, *_ = [int(n) for n in id.split('_')]

                    # Get parent comment (and the parent reply, if form belonged to reply)
                    # Also, determine which is the parent: a comment or a reply.
                    # If reply_num is 0, that means a comment is the parent
                    # because the dropdown form was submitted on a comment.
                    # But if reply_num > 0, then parent is a reply.
                    parent_comment = active_comments[comment_num]
                    if reply_num > 0:
                        parent_reply = parent_comment.replies.all()[reply_num - 1]
                        parent = parent_reply
                    else:
                        parent = parent_comment

                    # Get action performed by dropdown form
                    action = request.POST.get('action', '')

                    # CREATE NEW REPLY
                    if action == 'create_reply':

                        # Create reply object but don't save to database yet
                        new_reply = dropdown_form.save(commit=False)

                        # Assign the current post to the comment
                        new_reply.comment = parent_comment
                        new_reply.author = user

                        # Also, add handle
                        new_reply.handle = "@" + parent.author.first_name

                        # Save the comment to the database
                        new_reply.save()

                        # Check if replier is author of original comment
                        user_is_par_comment_author = (user == parent_comment.author)
                        user_is_par_reply_author = (user == parent_comment.author)

                        # If user is not author of the parent object, and
                        # the parent is set for notifications, send notice
                        # to the author of the parent object
                        if parent.author != user and parent.notify:
                            send_reply_notice(parent, new_reply)

                        # If the author of the parent object is not the
                        # author of the parent comment, then the author of
                        # the parent comment has not been notified yet. So,
                        # notify them too if the parent comment is set
                        # for notifications.
                        if parent.author != parent_comment.author and parent_comment.notify:
                            send_reply_notice(parent_comment, new_reply)

                    # EDIT COMMENT/REPLY
                    elif action == 'create_edit':

                        # Proceed only if current logging in user's name and email
                        # matches the author's of the reply the user is trying to edit.
                        # In other words, make sure if user is editing their own reply.
                        if parent.is_author(user):

                            # Check if edit is to delete the reply. Delete it if so
                            if request.POST.get('is_deletion', '') == 'true':
                                parent.active = False
                                parent.deactivated_on = timezone.now()
                                parent.save()

                            # If not to delete, then save changes
                            else:

                                # Create reply object but don't save to database
                                edit = dropdown_form.save(commit=False)

                                # Update parent reply to have the body of the edit
                                parent.body = edit.body
                                parent.edited = True
                                parent.save()

            # Reload page at the comment section
            return HttpResponseRedirect(reverse('posts:show', kwargs={'slug': slug}) + '#comments')

        # Define other parameters
        comment_form = CommentForm()
        dropdown_form = DropdownForm()
        site_key = settings.RECAPTCHA_SITE_KEY

        # Render agpost with all comments/replies,
        # and with recaptcha site key
        return render(request, 'agpost.html', {'agpost': req_agpost, 'active_comments': active_comments,
                                               'comment_form': comment_form, 'dropdown_form': dropdown_form,
                                               'site_key': site_key})


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
