from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress
from django.http import HttpResponseRedirect
from django.urls import reverse


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

        print("checking if email already exists")
        print("email:", sociallogin.account.extra_data['email'])
        # social account already exists, so this is just a login
        if sociallogin.is_existing:
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

        # check if given email address already exists as a verified email on
        # an existing user's account
        try:
            existing_email = EmailAddress.objects.get(email__iexact=email.email, verified=True)
        except EmailAddress.DoesNotExist:
            return

        print("email does exist! connecting social account to exisint account")
        # if it does, connect this new social login to the existing user
        sociallogin.connect(request, existing_email.user)