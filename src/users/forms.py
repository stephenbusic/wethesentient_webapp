from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django import forms


class CreatePassword(forms.Form):

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
        'password_weak': _("Password must be at least 8 characters."),
    }
    password1 = forms.CharField(label="",
                                widget=forms.PasswordInput(
                                attrs={'placeholder': 'Password'}),)

    password2 = forms.CharField(label="",
                                widget=forms.PasswordInput(
                                attrs={'placeholder': 'Confirm password'}),)

    class Meta:
        fields = ("password",)

    def clean_password2(self):

        # Get inputs
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        # Throw error if they don't match
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        # Throw error if the passwords are two short
        if len(password2) < 8:
            raise forms.ValidationError(
                self.error_messages['password_weak'],
                code='password_weak',
            )
        return password2


class LoginUser(forms.Form):

    error_messages = {
        'invalid_login': _("Invalid login."),
    }
    email = forms.EmailField(label="",
                                widget=forms.EmailInput(
                                attrs={'placeholder': 'Email'}),)

    password = forms.CharField(label="",
                                widget=forms.PasswordInput(
                                attrs={'placeholder': 'Password'}),)

    class Meta:
        fields = ("email", "password",)

    def clean_email(self):

        email = self.cleaned_data.get("email")
        try:
            match = User.objects.get(email=email)
            return email
        except User.DoesNotExist:
            return None
            # Error gets raised by clean_password
            # so no need to raise one here


    def clean_password(self):

        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if self.is_pword(email=email, password=password):
            return password
        else:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
            )

    def is_pword(self, email=None, password=None):
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return True
            return False
        except User.DoesNotExist:
            return False


class SendPasswordReset(forms.Form):

    error_messages = {
        'invalid_email': _("Invalid email."),
    }

    email = forms.EmailField(label="",
                                widget=forms.EmailInput(
                                attrs={'placeholder': 'Email'}),)

    class Meta:
        fields = ("email",)

    # Return email entered for password reset
    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email
