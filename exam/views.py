from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from .forms import CustomAuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import views as auth_views

from .tokens import account_activation_token
from .forms import PlatformForm, MyUserCreationForm, SetPasswordFormPL
from .models import Platform, Activity
# Create your views here.
class HomepageView(TemplateView):
    template_name = "homepage.html"

class HomeLoginView(LoginView):
    template_name = "login.html"
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy("exam:home-redirect")

class RedirectHomepage(View):
    def get(self, request):
        Activity(kind="visit").save()
        if hasattr(request.user.groups.first(), "name"):
            if request.user.groups.first().name == "Platform_Admin":
                if request.user.is_active:
                    try:
                        Platform.objects.get(users=request.user)
                        return redirect(reverse_lazy("platform_admin:homepage"))
                    except:
                        return redirect(reverse_lazy("exam:create-platform"))                     
                else:
                    return redirect (reverse_lazy("exam:homepage"))
            elif request.user.groups.first().name == "Examiner":
                return redirect (reverse_lazy("examiner_user:homepage"))
            elif request.user.groups.first().name == "Student":
                return redirect (reverse_lazy("student:homepage"))
            else:
                return redirect (reverse_lazy("exam:homepage"))
        else:
            return redirect (reverse_lazy("exam:homepage"))

class RegistraitionView(View):
    template_name = "registration.html"

    def add_to_platform_admin_group(self, user):
        """adds user to platform admin group and marks them as inactive"""
        user.is_active = False
        group = get_object_or_404(Group, name="Platform_Admin")
        group.user_set.add(user)
        user.save()

    def send_registraition_mail(self, request, user, mail):
        current_site = get_current_site(request)
        mail_subject = 'Aktywuj swoje konto na Examinerze'
        message = render_to_string('activate_email.html', {
            'user': user,
            'domain': current_site.domain,
            'pk': user.pk,
            'token':account_activation_token.make_token(user),
        })
        email = EmailMessage(mail_subject, message, to=[mail])
        email.send()

    def get(self, request):
        user_form = MyUserCreationForm()
        context = {"user_form" : user_form,}
        return render(request, self.template_name, context)
    
    def post(self, request):
        Activity(kind="registration").save()
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            self.add_to_platform_admin_group(user)
            mail = form.cleaned_data.get('email')
            self.send_registraition_mail(request, user, mail)
            messages.info(request, "Email informacyjny został wysłany, prosimy sprawdzić skrzynkę pocztową")
        else:
            messages.error(request, "Niepoprawne dane, możliwe że nazwa użytkownika jest zajęta")
        return redirect(reverse_lazy("exam:homepage"))

class ActivateView(View):
    def get(self, request, *args, **kwargs):
        user = User.objects.get(pk=self.kwargs["pk"])
        if user is not None and account_activation_token.check_token(user, self.kwargs["token"]):
            user.is_active = True
            user.save()
            login(request, user)
            return redirect(reverse_lazy("exam:home-redirect"))
        else:
            messages.error(request, "Kod aktywacyjny jest niepoprawny")
            return redirect(reverse_lazy("exam:homepage"))

class PlatformCreate(View):
    template_name = "create_platform.html"
    form = PlatformForm

    def get(self, request, *args, **kwargs):
        form = self.form()
        context = {"form":form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        if form.is_valid():
            form.save()
            platform = Platform.objects.all().last()
            platform.users.add(request.user)
            platform.save()
            return redirect(reverse_lazy("platform_admin:homepage"))

class PasswordReset(auth_views.PasswordResetView):
    template_name = "password_reset.html"
    email_template_name = "reset_mail.html"
    def get_success_url(self):
        return (reverse_lazy("exam:password-reset-done"))

class ResetDone(auth_views.PasswordResetDoneView):
    template_name = "password_reset_sent.html"

class ResetConfirm(auth_views.PasswordResetConfirmView):
    form_class = SetPasswordFormPL
    template_name = "password_reset_confirm.html"
    def get_success_url(self):
        return (reverse_lazy("exam:password-reset-complete"))

class ResetComplete(auth_views.PasswordResetCompleteView):
    template_name = "password_reset_complete.html"

class ActivityView(View):
    template_name = "activity.html"

    def get(self, request, *args, **kwargs):
        activities = Activity.objects.all()[::-1]
        context = {"activities" : activities}
        return render(request, self.template_name, context)