from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import HomepageView, HomeLoginView, RedirectHomepage

app_name="exam"
urlpatterns = [
    path("homepage/", HomepageView.as_view(), name="homepage"),
    path("login/", HomeLoginView.as_view(), name = "login"),
    path("logout/", LogoutView.as_view(template_name = "homepage.html"), name="logout"),
    path("home/redirect/", RedirectHomepage.as_view(), name="home-redirect")
]