from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.models import EmailAddress


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

        # social account already exists, so this is just a login.
        # Or could be previously deleted user returning, in which
        # case reactivate them.
        if sociallogin.is_existing:
            user = sociallogin.user
            if user.activate == False:
                user.activate = True
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
        # an existing user's account. Return if not.
        try:
            email = verified_email.lower()
            existing_email = EmailAddress.objects.get(email__iexact=email)

        except EmailAddress.DoesNotExist:
            return

        # Get the existing social account user
        sameUser_OtherSocialAccount = existing_email.user

        # Connect this new social login to the existing user
        sociallogin.connect(request, sameUser_OtherSocialAccount)