from django.urls import path
from account.views import profile, Update_account, bookmarks


app_name = 'account'

urlpatterns = [
    path('<int:pk>', profile, name='profile'),
    path('<int:pk>/edit', Update_account, name='edit'),
    path('bookmarks', bookmarks, name='bookmarks'),
  ]
