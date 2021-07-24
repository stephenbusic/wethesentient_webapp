from django import template

register = template.Library()


# Register the template tag for checking
# if a user is the author of a given comment
@register.simple_tag
def is_comment_author(comment, user):
    return user == comment.author


# Register the template tag for checking
# if a user is the author of a given reply
@register.simple_tag
def is_reply_author(reply, user):
    return user == reply.author
