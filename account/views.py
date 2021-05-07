from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from account.forms import RegisterationForm, LoginForm, AccountUpdateForm
from account.models import Account
from posts.models import Post, SharedPost
from django.db.models import Q
from friend.models import FriendList, FriendRequest
from friend.utils import get_friend_request_or_false
from friend.FRIEND_REQUEST_STATUS import FriendRequestStatus
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.core.paginator import Paginator
# from django.core import files
#
#
# TEMP_PROFILE_IMAGE_NAME = "temp_profile_image.png"

@receiver(user_logged_in)
def got_online(sender, user, request, **kwargs):
    user.is_online = True
    user.save()

@receiver(user_logged_out)
def got_offline(sender, user, request, **kwargs):
    user.is_online = False
    user.save()

def register_view(request, *args, **kwargs):
    user = request.user
    if user.is_authenticated:
        return redirect('home')

    context = {}
    if request.POST:
        form = RegisterationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email').lower()
            raw_password = form.cleaned_data.get('password1')
            account = authenticate(email=email, password=raw_password)
            login(request, account)

            destination = get_redirect_if_exists(request)
            if destination: #if destination is != None
                return redirect(destination)
            else:
                return redirect('home')
        else:
            context['registration_form'] = form

    return render(request, 'account/register.html', context)

def login_view(request, *args, **kwargs):
    context = {}

    if request.user.is_authenticated:
        return redirect('home')


    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(email = email, password = password)
            if user:
                login(request, user)
                destination = get_redirect_if_exists(request)
                if destination:
                    return redirect(destination)
                else:
                    return redirect('home')
        else:
            context['login_form'] = form
    return render(request, 'account/login.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

def get_redirect_if_exists(request):
    redirect = None
    if request.GET:
        if request.GET.get("next"):
            redirect = str(request.GET.get('next'))
        return redirect

@login_required
def profile(request, *args, **kwargs):
    context = {}
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
    friend_requests = None
    user_id = kwargs.get('pk')
    try:
        account = Account.objects.get(pk = user_id)
    except Account.DoesNotExist:
        return render(request, 'snippets/404.html')

    if account:
        all_posts = []
        own_posts = Post.objects.filter(user=account).order_by('-published_date')
        shared_posts = SharedPost.objects.filter(user = account)

        for post in own_posts:
            all_posts.append((post,'own', '', post.published_date))

        for post in shared_posts:
            all_posts.append((post.post,'shared', post.user, post.date_shared, post.quote, post.id))

        all_posts = sorted(all_posts, key=lambda post: post[3], reverse=True)

        paginator = Paginator(all_posts, 3)
        page = request.GET.get('page')
        posts = paginator.get_page(page)


        context['posts'] = posts
        context['id'] = account.id
        context['username'] = account.username
        context['first_name'] = account.first_name
        context['last_name'] = account.last_name
        context['bio'] = account.bio
        context['email'] = account.email
        context['profile_img'] = account.profile_img
        context['hide_email'] = account.hide_email
        context['is_private'] = account.is_private
        context['get_online_status'] = account.get_online_status()
        context['last_login'] = account.last_login



        #define state template variables
        try:
            friend_list = FriendList.objects.get(user=account)
        except FriendList.DoesNotExist:
            friend_list = FriendList(user=account)
            friend_list.save()
        friends = friend_list.friends.all()
        context['friends'] = friends


        is_self = True
        is_friend = False
        user = request.user

        if user.is_authenticated and user != account:
            is_self = False
            if friends.filter(pk=user.id):
                is_friend = True

            else:
                is_friend = False
                friend_request = get_friend_request_or_false(sender = account, receiver = user)
                if  friend_request != False:
                    request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
                    context['pending_friend_request_id'] = friend_request.id
                    context['request_timestamp'] = friend_request.timestamp


                elif get_friend_request_or_false(sender = user, receiver = account) != False:
                    request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
                else:
                    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value

        elif not user.is_authenticated:
            is_self = False

        else:
            try:
                friend_requests = FriendRequest.objects.filter(receiver=user, is_active=True)
            except:
                pass

        context['is_self'] = is_self
        context['is_friend'] = is_friend
        context['BASE_DIR'] = settings.BASE_DIR
        context['request_sent'] = request_sent
        context['friend_requests'] = friend_requests
        context['account'] = account

    return render(request, 'account/account_rtl.html', context)

@login_required
def account_search(request, *args, **kwargs):
    context = {}
    user = request.user
    if request.GET:
        search_query = request.GET.get('q')
        if len(search_query) > 0:
            search_results = Account.objects.filter(
            Q(email__icontains = search_query) | Q(username__icontains = search_query)).distinct()
            accounts = []
            auth_user_friend_list = FriendList.objects.get(user=user)
            for account in search_results:
                accounts.append((account, auth_user_friend_list.is_mutual_friend(account)))
            context['accounts'] = accounts

    return render(request, 'account/search_results.html', context)

# def save_temp_profile_image_from_base64String(imageString, user):
# 	INCORRECT_PADDING_EXCEPTION = "Incorrect padding"
# 	try:
# 		if not os.path.exists(settings.TEMP):
# 			os.mkdir(settings.TEMP)
# 		if not os.path.exists(settings.TEMP + "/" + str(user.pk)):
# 			os.mkdir(settings.TEMP + "/" + str(user.pk))
# 		url = os.path.join(settings.TEMP + "/" + str(user.pk),TEMP_PROFILE_IMAGE_NAME)
# 		storage = FileSystemStorage(location=url)
# 		image = base64.b64decode(imageString)
# 		with storage.open('', 'wb+') as destination:
# 			destination.write(image)
# 			destination.close()
# 		return url
# 	except Exception as e:
# 		print("exception: " + str(e))
# 		# workaround for an issue I found
# 		if str(e) == INCORRECT_PADDING_EXCEPTION:
# 			imageString += "=" * ((4 - len(imageString) % 4) % 4)
# 			return save_temp_profile_image_from_base64String(imageString, user)
# 	return None
#
#
#
# def crop_image(request, *args, **kwargs):
# 	payload = {}
# 	user = request.user
# 	if request.POST and user.is_authenticated:
# 		try:
# 			imageString = request.POST.get("image")
# 			url = save_temp_profile_image_from_base64String(imageString, user)
# 			img = cv2.imread(url)
#
# 			cropX = int(float(str(request.POST.get("cropX"))))
# 			cropY = int(float(str(request.POST.get("cropY"))))
# 			cropWidth = int(float(str(request.POST.get("cropWidth"))))
# 			cropHeight = int(float(str(request.POST.get("cropHeight"))))
# 			if cropX < 0:
# 				cropX = 0
# 			if cropY < 0: # There is a bug with cropperjs. y can be negative.
# 				cropY = 0
# 			crop_img = img[cropY:cropY+cropHeight, cropX:cropX+cropWidth]
#
# 			cv2.imwrite(url, crop_img)
#
# 			# delete the old image
# 			user.profile_image.delete()
#
# 			# Save the cropped image to user model
# 			user.profile_image.save("profile_image.png", files.File(open(url, 'rb')))
# 			user.save()
#
# 			payload['result'] = "success"
# 			payload['cropped_profile_image'] = user.profile_image.url
#
# 			# delete temp file
# 			os.remove(url)
#
# 		except Exception as e:
# 			print("exception: " + str(e))
# 			payload['result'] = "error"
# 			payload['exception'] = str(e)
# 	return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required
def Update_account(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect('login')

    user_id = kwargs.get('pk')
    try:
        account = Account.objects.get(pk = user_id)
    except account.DoesNotExist:
        return render(request, 'snippets/404.html')
    if request.user.id != account.pk:
        return render(request, 'snippets/404.html')
    context = {}
    if request.POST:
        form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('account:profile', pk=account.pk)
        else:
            form = AccountUpdateForm(request.POST, request.FILES, instance=request.user)
            context['form'] = form
    else:
        form = AccountUpdateForm(instance=request.user)
        context['form'] = form

    context['DATA_UPLOAD_MAX_MEMORY_SIZE'] = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
    return render(request, 'account/edit_account.html', context)


@login_required
def bookmarks(request):
    user = request.user
    bookmarks = user.bookmark.posts.all()

    paginator = Paginator(bookmarks, 10)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
      'bookmarks': posts,
      'account': user
    }

    return render(request, 'account/bookmarks.html', context)
