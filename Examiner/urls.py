"""Examiner URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from exam.views import RedirectHomepage, RedirectHomepage
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve

urlpatterns = i18n_patterns(
    path("", RedirectHomepage.as_view(), name="homepage"),
    path('admin/', admin.site.urls),
    path('home/', include ("exam.urls")),
    path('student/', include ("student.urls")),
    path('examiner/', include ("examiner_user.urls")),
    path('platform/', include ("platform_admin.urls")),
    path("accounts/profile/", RedirectHomepage.as_view(), name="login-redirect"),
    path('media/', serve,{'document_root': settings.MEDIA_ROOT})
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)