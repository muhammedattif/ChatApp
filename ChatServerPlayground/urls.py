"""ChatServerPlayground URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from personal.views import (
    home,messenger
)
from account.views import (
    register_view,
    login_view,
    logout_view,
    profile,
    account_search
)

from django.contrib.auth import views as auth_views
from django.conf.urls import include
urlpatterns = [
    path('admin/timeline/', include('admin_timeline.urls')),

    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/',register_view , name='register'),
    path('login/',login_view , name='login'),
    path('logout/',logout_view , name='logout'),
    path('account/', include('account.urls', namespace='account')),
    path('account_search',account_search , name='search'),
    path('friend/', include('friend.urls', namespace='friend')),
    path('posts/', include('posts.urls', namespace='posts')),
    path('messenger/<str:username>/',messenger , name='messenger'),



    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='account/password_reset/password_change_done.html'),
        name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='account/password_reset/password_change.html'),
        name='password_change'),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset/password_reset_done.html'),
     name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='account/password_reset/password_reset.html'), name='password_reset'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset/password_reset_complete.html'),
     name='password_reset_complete'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
