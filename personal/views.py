from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from account.models import Account
from posts.models import Post, SharedPost
from friend.models import FriendList
from posts.forms import PostModelForm
from chat.models import Thread, Message
from django.db.models import Q
from django.core.paginator import Paginator

# Create your views here.
@login_required
def home(request):
    allposts = []
    account = request.user
    friends_ids = account.friends.values_list("user__id", flat=True)
    friends_ids = list(friends_ids)
    friends_ids.append(account.id)
    friends_own_posts = Post.objects.filter(user__id__in = friends_ids ).exclude(privacy = 'private')
    #return posts shared by friends execlude posts of not matual friends
    friends_shared_posts = SharedPost.objects.filter(user__id__in = friends_ids, ).exclude(~Q(post__user__id__in = friends_ids),~Q(post__user__id = account.id) )

    for post in friends_own_posts:
        allposts.append((post,'own', '', post.published_date))

    for post in friends_shared_posts:
        allposts.append((post.post,'shared', post.user, post.date_shared, post.quote, post.id))

    allposts = sorted(allposts, key=lambda post: post[3], reverse=True)

    paginator = Paginator(allposts, 3)
    page = request.GET.get('page')
    posts = paginator.get_page(page)



    form = PostModelForm()
    context = {
      'account': account,
      'posts': posts,
      'form': form,

    }
    return render(request, 'personal/home.html', context)

@login_required
def messenger(request, *args, **kwargs):
    username = kwargs.get('username')
    try:
        friend = Account.objects.get(username = username)
    except Account.DoesNotExist:
        return render(request, 'snippets/404.html')


    if request.user.friend_list.is_mutual_friend(friend):
        thread = Thread.objects.get_or_create_personal_thread(request.user, friend)
        messages = Message.objects.filter(thread = thread).order_by('date_sent')
        lastmessage = messages.last()

        # paginator = Paginator(messages, 10)
        # page = request.GET.get('page')
        # if not page:
        #     page = paginator.num_pages
        # allmessages = paginator.get_page(page)
        # print(paginator.num_pages)

        context = {
          'user': request.user,
          'friend': friend,
          'messages': messages,
          'lastmessage':lastmessage
        }
        return render(request, 'personal/messenger.html', context)
    return render(request, 'snippets/404.html')
