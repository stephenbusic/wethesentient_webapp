from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils.text import slugify
from django.contrib.auth import get_user_model
from django.utils import timezone
from homepage.sub_email_utility import send_subs_new_post_email
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField
import random

User = get_user_model()


# function to dynamically creating upload path for uploaded images
def generate_imagepath(self, filename):
    url = "%s/%s" % (self.slug, filename)
    return url


# Generate unique ID number for agpost
def create_new_ref_number():
    not_unique = True
    while not_unique:
        unique_ref = random.randint(100000, 999999)
        if not AGPost.objects.filter(ref_number=unique_ref):
            not_unique = False
    return unique_ref


# Model for AAAHHH ghosts post
class AGPost(models.Model):
    title = models.CharField(max_length=160)
    author = models.CharField(max_length=150, default="Stephen Busic")
    slug = models.SlugField(max_length=160)
    desc = RichTextField(max_length=750)
    body = RichTextUploadingField()
    has_sources = models.BooleanField(default=True)
    sources = RichTextUploadingField(blank=True)
    type = models.CharField(max_length=160)
    date = models.DateField(auto_now_add=True)
    thumb = models.ImageField(upload_to=generate_imagepath, default='default_thumb.jpg', blank=True)
    square_thumb = models.ImageField(upload_to=generate_imagepath, default='default_square_thumb.jpg', blank=True)
    email_subs = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    ref_number = models.IntegerField(default=create_new_ref_number)

    class Meta:
        ordering = ['-date']
        verbose_name_plural = "AGPosts"
        permissions = [
            ("can_comment_or_reply", "Can create comments or replies"),
        ]

    def __str__(self):
        return self.title

    # Auto generate post details
    def save(self, *args, **kwargs):

        # If saving for the first time
        if self._state.adding:

            # Generate unique slug for post url
            new_slug = slugify(self.title)

            unique = False
            initial_new_slug = new_slug
            i = 1
            while not unique:
                if AGPost.objects.filter(slug=new_slug).exists():
                    new_slug = initial_new_slug
                    new_slug += str(i)
                else:
                    unique = True
                i += 1
            self.slug = new_slug
        super(AGPost, self).save()


# Create receiver to listen for when new posts are created.
@receiver(post_save, sender=AGPost)
def announce_post(sender, **kwargs):
    if kwargs['created']:
        agpost = kwargs.get('instance')

        # Email subscribers if post is set to.
        if agpost.email_subs:
            send_subs_new_post_email(agpost)


# Model for each comment on a post
class Comment(models.Model):
    agpost = models.ForeignKey(AGPost, null=True, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=4000)
    created_on = models.DateTimeField(auto_now_add=True)
    deactivated_on = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    notify = models.BooleanField(default=False)
    rank = models.IntegerField(default=10)
    pinned = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['agpost']

    def __str__(self):

        preview = self.body
        if len(preview) > 25:
            preview = preview[0:25] + "..."

        return '"{}" by {} on: {}'.format(preview, self.author.get_full_name(), self.agpost.title)

    # Updated pin status on each save
    def save(self, *args, **kwargs):

        # If ranked high, pin comment
        if self.rank < 10:
            self.pinned = True
        else:
            self.pinned = False

        # If deactivated, record date
        if not self.active:
            self.deactivated_on = timezone.now()

        super(Comment, self).save()

    # Method for determining if given user is
    # the author of the comment
    def is_author(self, user):
        if user.is_authenticated:
            return user is self.author
        else:
            return False


# Model for reach reply on a comments
class Reply(models.Model):
    comment = models.ForeignKey(Comment, null=True, on_delete=models.CASCADE, related_name='replies')
    author = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField(max_length=4000)
    handle = models.CharField(max_length=90, default="", blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    deactivated_on = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(default=True)
    notify = models.BooleanField(default=True)
    rank = models.IntegerField(default=10)
    pinned = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)

    class Meta:
        ordering = ['comment', 'rank', 'created_on']
        verbose_name_plural = "Replies"

    def __str__(self):

        preview = self.body
        if len(preview) > 25:
            preview = preview[0:25] + "..."

        return '"{}" by {} on: {}\'s comment on {}'.format(preview, self.author.get_full_name(),
                                                           self.comment.author.get_full_name(), self.comment.agpost.title)

    # Updated pin status on each save
    def save(self, *args, **kwargs):

        # If rank high, pin reply
        if self.rank < 10:
            self.pinned = True
        else:
            self.pinned = False

        # If deactivated, record date
        if not self.active:
            self.deactivated_on = timezone.now()

        super(Reply, self).save()

    # Method for determining if given user is
    # the author of the comment
    def is_author(self, user):
        if user.is_authenticated:
            return user is self.author
        else:
            return False

