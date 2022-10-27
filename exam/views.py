from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView
from .forms import CustomAuthenticationForm
from django.contrib.auth.views import LoginView


# Create your views here.
class HomepageView(TemplateView):
    template_name = "homepage.html"

class HomeLoginView(LoginView):
    template_name = "login.html"
    form_class = CustomAuthenticationForm
    success_url = reverse_lazy("exam:home-redirect")

class RedirectHomepage(View):
    def get(self, request):
        if hasattr(request.user.groups.first(), "name"):
            if request.user.groups.first().name == "Examiner":
                return redirect (reverse_lazy("examiner_user:homepage"))
            elif request.user.groups.first().name == "Student":
                return redirect (reverse_lazy("student:homepage"))
            else:
                return redirect (reverse_lazy("exam:homepage"))
        else:
            return redirect (reverse_lazy("exam:homepage"))