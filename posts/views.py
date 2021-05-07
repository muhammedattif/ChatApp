from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.views.generic import View
from django.urls import reverse
from .models import Post, Comment, SharedPost
from django.core.paginator import Paginator
from django.conf import settings
from django.contrib import messages
from .forms import PostModelForm, SharedPostModelForm
from django.db.models import Q
from django.contrib.auth.decorators import login_required
# Create your views here.
User = settings.AUTH_USER_MODEL

# this function returns all published posts of all users (timeline)
@login_required()
def post(request, id):
    post = Post.objects.get(pk = id)

    context = {
        'post': post
    }
    return render(request, 'posts/post.html', context)

@login_required()
def like_post(request):
    payload = {}
    post_id = request.POST.get('post_id')
    account = request.user
    if post_id:
        try:
            post = Post.objects.get(pk=post_id)
            post.like(account)
            post.save()
            payload['response'] = 'success'
        except Post.DoesNotExist:
            return render(request, 'snippets/404.html')
    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required()
def unlike_post(request):
    payload = {}
    post_id = request.POST.get('post_id')
    account = request.user
    if post_id:
        try:
            post = Post.objects.get(pk=post_id)
            post.unlike(account)
            post.save()
            payload['response'] = 'success'
        except Post.DoesNotExist:
            return render(request, 'snippets/404.html')
    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")


# this function used to get all posts of a particular user and logedin user
def user_posts(request, user):
    auther = False
    # return published and unpublished posts for the post's auther
    if request.user.username == user:
        auther = True
        if request.method == 'POST':
            all_posts = Post.objects.filter(user__username = user, category = request.POST['category'])
        else:
            all_posts = Post.objects.filter(user__username = user)
    else:
        all_posts = Post.objects.filter(published = True, user__username = user)


    paginator = Paginator(all_posts, 3)
    page = request.GET.get('page')
    all_posts = paginator.get_page(page)
    categories = Category.objects.all()
    context = {
        'all_posts': all_posts,
        'categories': categories,
        'auther': auther
    }
    return render(request, 'user_posts.html', context)


@login_required()
def add_comment(request, *args, **kwargs):
    payload = {}
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        comment_text = request.POST.get('comment')
        print(comment_text)
        print(post_id)
        if comment_text and post_id:
            try:
                post = Post.objects.get(pk = post_id)
                comment = Comment.objects.create(
                user=request.user, post = post, comment = comment_text
                )
                payload['response'] = 'success'
            except Post.DoesNotExist:
                payload['response'] = 'error'
        else:
            payload['response'] = 'error'
    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required()
def like_comment(request):
    payload = {}
    comment_id = request.POST.get('comment_id')
    account = request.user
    if comment_id:
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.like(account)
            comment.save()
            payload['response'] = 'success'
        except Comment.DoesNotExist:
            return render(request, 'snippets/404.html')
    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")


@login_required()
def unlike_comment(request):
    payload = {}
    comment_id = request.POST.get('comment_id')
    account = request.user
    if comment_id:
        try:
            comment = Comment.objects.get(pk=comment_id)
            comment.unlike(account)
            comment.save()
            payload['response'] = 'success'
        except Comment.DoesNotExist:
            return render(request, 'snippets/404.html')
    else:
        payload['response'] = 'error'

    return HttpResponse(json.dumps(payload), content_type="application/json")

# display all comments received
@login_required()
def display_all_comments(request):
    comments = Comment.objects.filter(post__user=request.user)
    context = {
      'comments': comments
    }
    return render(request, 'all_posts_comments.html', context)


#CRUD
def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    comments = Comment.objects.filter(post__pk=pk)
    context = {
        'post': post,
        'comments': comments
    }
    if request.user == post.user:
        return render(request, 'post_details.html', context)
    else:
        post = get_object_or_404(Post, id=pk, published=True)

    return render(request, 'post_details.html', context)

@login_required()
def create_post(request):
    if request.method == 'POST':
        form = PostModelForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, "Post Created Successfully!!")
            return redirect('home')
        else:
            messages.error(request, "Post cannot be empty!")
            return redirect('home')
    return render(request, 'personal/home.html')

@login_required()
def update_post(request, id):
    context = {}
    post = get_object_or_404(Post, id=id)
    if request.user == post.user:
        if request.method == 'POST':
            form = PostModelForm(request.POST or None, request.FILES or None, instance=post)
            if form.is_valid():
                form.save()
                messages.success(request, "Post Updated Successfully!!")
                return redirect('home')
            else:
                messages.error(request, "Post cannot be empty!!")
                return redirect('home')

            return render(request, 'posts/update_post.html', context)

        else:
            form = PostModelForm(instance=post)
            context['form'] = form
            context['post_id'] = id
            return render(request, 'posts/update_post.html', context)
    else:
        return render(request, 'snippets/404.html')


@login_required()
def delete_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user == post.user:
        post.delete()
        messages.success(request, "Post Deleted Successfully!!")
        return redirect('home')
    else:
        messages.error(request, "Access Denied!")
        return redirect('home')


@login_required()
def share_post(request, id):
    if request.method == 'POST':
        try:
            post = Post.objects.get(~Q(privacy = 'private'), id=id)
        except Post.DoesNotExist:
            messages.error(request, "Access Denied!")
            return redirect('home')

        if post.user.friend_list.is_mutual_friend(request.user) or post.user == request.user:
            form = SharedPostModelForm(request.POST)
            if form.is_valid():
                form.instance.user = request.user
                form.instance.post = post
                form.save()
                messages.success(request, "Post Shared Successfully!!")
                return redirect('home')
            else:
                messages.error(request, "Something went Wrong!")
                return redirect('home')
        else:
            messages.error(request, "Access Denied!")
            return redirect('home')

@login_required()
def delete_shared_post(request, id):
    try:
        shared_post = SharedPost.objects.get(id=id, user=request.user)
        shared_post.delete()
        messages.success(request, "Post Deleted Successfully!!")
        return redirect('home')
    except SharedPost.DoesNotExist:
        messages.error(request, "Access Denied!")
        return redirect('home')

@login_required
def add_to_bookmark(request):
    payload = {}
    post_id = request.POST.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        payload['response'] = 'False'

    if post.user.friend_list.is_mutual_friend(request.user) or post.user == request.user:
        post.add_to_bookmark(request.user)
        payload['response'] = 'True'

    return HttpResponse(json.dumps(payload), content_type="application/json")

@login_required
def remove_from_bookmark(request):
    payload = {}
    post_id = request.POST.get('post_id')
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        payload['response'] = 'False'

    if post.user.friend_list.is_mutual_friend(request.user) or post.user == request.user:
        post.remove_from_bookmark(request.user)
        payload['response'] = 'True'

    return HttpResponse(json.dumps(payload), content_type="application/json")


class JSONCommentsListView(View):
    def get(self, *args, **kwargs):
        post_id = kwargs.get('post_id')
        upper = kwargs.get('num_comments')
        lower = upper - 3
        comments = list(Post.objects.get(pk=post_id).comments.select_related().values()[lower:upper])
        return JsonResponse({'data':comments}, safe=False)
