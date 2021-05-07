from django.shortcuts import render
from django.http import HttpResponse
from account.models import Account
from friend.models import FriendRequest, FriendList
import json
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def friend_list(request, *args, **kwargs):
    context = {}
    user = request.user
    user_id = kwargs.get('user_id')
    if user_id:
        try:
            this_account = Account.objects.get(pk=user_id)
            context = {
              'this_account': this_account
            }
        except Account.DoesNotExist:
            return render(request, 'snippets/404.html')

        try:
            friend_list = FriendList.objects.get(user=this_account)

        except FriendList.DoesNotExist:
            pass

        #must be friends to view friend list
        if user != this_account:
            if not user in friend_list.friends.all():
                return render(request, 'snippets/404.html')

        friends = [] #[(account, false), (account, True)]
        auth_user_friend_list = FriendList.objects.get(user=user)
        for friend in friend_list.friends.all():
            friends.append((friend, auth_user_friend_list.is_mutual_friend(friend)))

        context['friends'] = friends
        context['username'] = this_account.username
    else:
        return render(request, 'snippets/404.html')

    return render(request, 'friend/friend_list.html', context)


@login_required
def friend_requests(request, *args, **kwargs):
    context = {}
    user = request.user
    if user.is_authenticated:
        user_id = kwargs.get('user_id')
        try:
            account = Account.objects.get(pk=user_id)

            if user == account:
                friend_requests = FriendRequest.objects.filter(receiver=account, is_active=True)
                context = {
                  'friend_requests': friend_requests
                }
            else:
                return render(request, 'snippets/404.html')
        except Account.DoesNotExist:
            return render(request, 'snippets/404.html')

    else:
        return redirect('login')
    return render(request, 'friend/friend_requests.html', context)





@login_required
def send_friend_request(request, *args, **kwargs):
    sender = request.user
    payload = {}
    if request.method == "POST" and request.user.is_authenticated:
        user_id = request.POST.get('receiver_id')
        if user_id:
            receiver = Account.objects.get(pk=user_id)
            try:
                #get all the friend requests
                print("check friend requests")
                friend_requests = FriendRequest.objects.filter(sender=sender, receiver=receiver)

                #find if any one is active
                for request in friend_requests:
                    print("loop")
                    if request.is_active:
                        print("active")
                        #if there is already an active request
                        payload['response'] = "error"


                #if none are active, then sent a request
                friend_request = FriendRequest(sender=sender, receiver=receiver)
                friend_request.save()
                payload['response'] = "success"


            #if none are active, then sent a request
            except FriendRequest.DoesNotExist:
                print("check friend requests2")
                friend_request = FriendRequest(sender=sender, receiver=receiver)
                friend_request.save()
                payload['response'] = "success"

            if payload['response'] == None:
                payload['response'] = "Something went wrong."
        else:
            payload['response'] = "Something went wrong."
    else:
        payload['response'] = "You have to login to sent a friend request."

    return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required
def cancel_friend_request(request, *args, **kwargs ):
    sender = request.user
    payload = {}
    if request.method == "POST" and request.user.is_authenticated:
        receiver_id = request.POST.get('receiver_id')
        if receiver_id:
            receiver = Account.objects.get(pk=receiver_id)
            try:
                friend_request = FriendRequest.objects.get(sender=sender, receiver=receiver, is_active = True)

                friend_request.cancel()
                payload['response'] = 'deleted'
            except FriendRequest.DoesNotExists:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'
    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required
def decline_friend_request(request, *args, **kwargs):
    receiver = request.user
    payload = {}
    if request.method == "POST" and request.user.is_authenticated:

        request_id = request.POST.get('friend_request_id')
        if request_id:

            try:
                friend_request = FriendRequest.objects.get(pk=request_id)
                if friend_request.receiver == receiver:
                    friend_request.decline()
                    payload['response'] = 'declined'
                else:
                    payload['response'] = 'error'

            except FriendRequest.DoesNotExists:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'
    else:
        payload['response'] = 'error'
    return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required
def confirm_friend_request(request, *args, **kwargs):
    receiver = request.user
    payload = {}
    if request.method == "POST" and request.user.is_authenticated:
        request_id = request.POST.get('friend_request_id')
        if request_id:
            try:
                friend_request = FriendRequest.objects.get(pk=request_id)
                if friend_request.receiver == receiver:
                    friend_request.accept()
                    payload['response'] = 'confirmed'

            except FriendRequest.DoesNotExist:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'

    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required
def unfriend(request, *args, **kwargs):
    user = request.user
    payload = {}
    if request.method == "POST" and user.is_authenticated:
        user_id = request.POST.get("receiver_user_id")
        print(user_id)
        if user_id:
            try:
                removee = Account.objects.get(pk=user_id)
                friend_list = FriendList.objects.get(user=user)
                friend_list.unfriend(removee)
                payload['response'] = "Successfully removed that friend."
            except Account.DoesNotExist:
                payload['response'] = f"Something went wrong: {str(e)}"
        else:
            payload['response'] = 'There was an error. Unable to remove that friend'
    else:

        payload['response'] = "You must be authenticated to remove a friend."
    return HttpResponse(json.dumps(payload), content_type="application/json")
