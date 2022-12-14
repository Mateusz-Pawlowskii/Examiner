from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django import forms

from .models import Platform


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=None, *args, **kwargs)
        self.fields['username'].label = 'Login'
        self.fields['password'].label = 'Hasło'

class PlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ["name"]
    name = forms.CharField(label="", widget=forms.Textarea(attrs={'name':'text', 'rows':4, 'cols':200}))

class MyUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class SetPasswordFormPL(SetPasswordForm):
    new_password1 = forms.CharField(label=("Nowe hasło"))
    new_password2 = forms.CharField(label=("Potwierdzenie hasła"))