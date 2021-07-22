from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from allauth.socialaccount.forms import SignupForm
from django.forms import *


# from allauth.account.models import EmailAddress


class NoNewUsersAccountAdapter(DefaultAccountAdapter):
    """
    Adapter to disable allauth new signups
    Used at equilang/settings.py with key ACCOUNT_ADAPTER

    https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-redirects """

    def is_open_for_signup(self, request):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return False


class YesNewUsersSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Adapter to disable allauth new signups
    Used at equilang/settings.py with key SOCIALACCOUNT_ADAPTER

    https://django-allauth.readthedocs.io/en/latest/advanced.html#custom-redirects """

    def is_open_for_signup(self, request, sociallogin):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse
        """
        return True

    def pre_social_login(self, request, sociallogin):

        # Check if social account already exists, so this is just a login.
        # Or could be previously deleted user returning, in which
        # case reactivate them.
        if sociallogin.is_existing:
            user = sociallogin.user
            if not user.is_active:
                user.is_active = True
            return

        # some social logins don't have an email address
        if not sociallogin.email_addresses:
            return

        # find the first verified email that we get from this sociallogin
        verified_email = None
        for email in sociallogin.email_addresses:
            if email.verified:
                verified_email = email
                break

        # no verified emails found, nothing more to do
        if not verified_email:
            return

        # Social accounts are all linked to a single django user account for each user.
        # Try to see if verified email from attempted social login already exists as
        # a django user account. If not, return.
        try:
            # email = sociallogin.account.extra_data['email'].lower()
            # existing_email = EmailAddress.objects.get(email__iexact=verified_email)
            existingAccount = User.objects.get(email=verified_email)

        except User.DoesNotExist:
            return

        # Connect this new social login to the existing user
        sociallogin.connect(request, existingAccount)


class CustomSocialSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sociallogin = kwargs.pop('sociallogin')
        if 'email' in sociallogin.account.extra_data:
            self.initial['email'] = sociallogin.account.extra_data['email']
            self.fields['email'].disabled = True

    full_name = CharField(max_length=40, label='Full Name (With title, if applicable/desired)', required=True)

    def custom_signup(self, request, user):

        # Get name from form
        name = self.cleaned_data['full_name']

        # Ensure full name is unique
        counter = 1
        full_name = name
        while User.objects.filter(first_name__iexact=full_name):
            full_name = name + str(counter)
            counter += 1
        user.first_name = full_name

        # Ensure full name is unique
        counter = 1
        username = full_name.replace(' ', '_').lower()
        while User.objects.filter(first_name__iexact=username):
            user.first_name = full_name + str(counter)
            counter += 1
        user.username = username
        user.save()

        return user
