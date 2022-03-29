from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Prefetch, Count
from django.db.models.functions import TruncDay
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from homepage.views import process_sub_form
from posts.models import AGPostView, Reply
from users.user_email_utility import send_reply_notice
from common.util.recaptcha_utility import pass_recaptcha
from .forms import CommentForm, DropdownForm
from .models import AGPost


# View to display all existing agposts
def allposts(request, page_num):

    # Get all active agposts
    listed_agposts = AGPost.objects.filter(unlisted=False).order_by('-date')

    # Create paginator to show 4 posts per page
    paginator = Paginator(listed_agposts, 4)
    page_obj = paginator.get_page(page_num)

    # Render all agposts page
    return render(request, 'allposts.html', {'listed_agposts': page_obj, })


# View to show a given agpost
def show_post(request, slug):
    req_agpost = find_agpost(slug)

    if req_agpost is None:
        error_msg = "Sorry! Post not found :("
        return render(request, 'msgpage.html', {'msg': error_msg})
    else:

        # Get all active comments, and for each active
        # comment, get all active replies
        active_comments = req_agpost.comments.filter(active=True) \
            .order_by('rank', '-created_on').prefetch_related(
            Prefetch(
                'replies',
                queryset=Reply.objects.filter(active=True),
                to_attr='active_replies'
            )
        )

        # First, determine if sub_form was submitted. Before this can
        # be done, we need determine if the request is valid by checking if:
        # 1) request is of method POST
        # 2) request passes recaptcha test
        if request.method == 'POST' and pass_recaptcha(request):
            print("here??")
            # CREATE NEW SUB
            if 'create_subscription' in request.POST:

                # If new subscription is being created, then
                # we're done - just hand off request to homepage
                return process_sub_form(request)

            # Else, if not new sub, move on by getting current user
            user = request.user

            # Proceed to check for a new comment/reply/edit
            # if and only if 2 user conditions are met:
            # 1) user is logged in
            # 2) user has permission to comment/reply/edit
            if user.is_authenticated and user.has_perm('posts.can_comment_or_reply'):

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
                        active_replies = parent_comment.replies.filter(active=True, author__is_active=True).all()
                        if reply_num > 0:
                            parent_reply = active_replies[reply_num - 1]
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
                            new_reply.handle_user = parent.author

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
                            if user == parent.author:

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
                                               'site_key': site_key, 'pk': req_agpost.pk})


# Function to try and find an existing agpost based on a given slug
def find_agpost(slug):
    try:
        return AGPost.objects.get(slug=slug)
    except AGPost.DoesNotExist:
        return None


# View called by ajax to record a page view
def record_post_view(request):

    # Proceed only if ajax request
    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax and request.method == 'POST':

        data = {'success': False}

        # Get agpost post to count view for
        pk = request.POST.get('agpost_pk', None)
        agpost = AGPost.objects.get(pk=pk)

        # If view hasn't alreay been made for this user,
        # create view instance and save
        if not AGPostView.objects.filter(
                agpost=agpost,
                session=request.session.session_key):
            view = AGPostView(agpost=agpost,
                              ip=request.META['REMOTE_ADDR'],
                              session=request.session.session_key)
            view.save()
        data['success'] = True

        return JsonResponse(data)

    error_msg = "Sorry! Post not found :("
    return render(request, 'msgpage.html', {'msg': error_msg})


# View called by ajax to fetch view data
def get_viewchart_data(request):

    is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    if is_ajax and request.method == 'GET':

        duration = 90
        now = timezone.now()
        time_threshhold = now - timezone.timedelta(days=duration)

        # Aggregate new views for the last x number of days
        agpost_views = (
            AGPostView.objects.filter(created_on__gt=time_threshhold)
            .annotate(date=TruncDay("created_on"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )
        total_views = len(AGPostView.objects.all())
        return JsonResponse({'chart_data': list(agpost_views),
                             'total_views': total_views})

    error_msg = "Sorry! Post not found :("
    return render(request, 'msgpage.html', {'msg': error_msg})