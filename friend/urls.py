from django.urls import path
from friend.views import (
        send_friend_request,
        cancel_friend_request,
        decline_friend_request,
        confirm_friend_request,
        unfriend,
        friend_requests,
        friend_list)

app_name = 'friend'

urlpatterns = [
    path('friend_request/',send_friend_request ,  name='friend_request'),
    path('cancel_friend_request/',cancel_friend_request ,  name='cancel_friend_request'),
    path('decline_friend_request/',decline_friend_request ,  name='decline_friend_request'),
    path('confirm_friend_request/',confirm_friend_request ,  name='confirm_friend_request'),
    path('unfriend/',unfriend ,  name='unfriend'),
    path('friend_requests/<int:user_id>',friend_requests ,  name='friend_requests'),
    path('friends/<int:user_id>',friend_list ,  name='friend_list'),

  ]
