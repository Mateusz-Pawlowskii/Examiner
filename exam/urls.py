from django.urls import path
from django.contrib.auth.views import LogoutView

from .views import HomepageView, HomeLoginView, RedirectHomepage, RegistraitionView, ActivateView, PlatformCreate

app_name="exam"
urlpatterns = [
    path("homepage", HomepageView.as_view(), name="homepage"),
    path("login", HomeLoginView.as_view(), name = "login"),
    path("logout", LogoutView.as_view(template_name = "homepage.html"), name="logout"),
    path("home/redirect", RedirectHomepage.as_view(), name="home-redirect"),
    path("register", RegistraitionView.as_view(), name="register"),
    path("activate/<int:pk>/<str:token>", ActivateView.as_view(), name="activate"),
    path("platform/create", PlatformCreate.as_view(), name="create-platform")
]