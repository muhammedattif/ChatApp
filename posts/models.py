from django.db import models

from django.conf import settings
import datetime
from django.db.models import F
# Create your models here.

User = settings.AUTH_USER_MODEL

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    likes = models.ManyToManyField(User,blank=True, related_name="likes")
    description = models.TextField(blank=False, null=False)
    image = models.ImageField(upload_to='posts_imgs/', null=True, blank=True)
    published = models.BooleanField(blank=False, null=False, default=True)
    published_date = models.DateTimeField(auto_now_add=True)
    # shares = models.ManyToManyField(User,blank=True, related_name="posts_shared")

    PRIVACY_CHOICES = (
        ('public', 'Public'),
        ('friends', 'Friends'),
        ('private', 'Only Me'),
    )
    privacy = models.CharField(max_length=10, choices=PRIVACY_CHOICES, default="public")

    class Meta:
        ordering = ['-published_date']



    def __str__(self):
        return "{}, {}".format(self.user.username,self.description)

    def is_public(self):
        return self.privacy == 'public'

    def is_private(self):
        return self.privacy == 'private'

    def like(self, account):
        if not account in self.likes.all():
            self.likes.add(account)

    def unlike(self, account):
        if account in self.likes.all():
            self.likes.remove(account)

    def get_path(self):
        return "/posts/post/{}".format(self.pk)

    def get_model_type(self):
        return 'post'

    def add_to_bookmark(self, account):
        bookmark, created = Bookmark.objects.get_or_create(user=account)
        bookmark.posts.add(self)
        bookmark.save()

    def remove_from_bookmark(self, account):
        bookmark, created = Bookmark.objects.get_or_create(user=account)
        if self in bookmark.posts.all():
            bookmark.posts.remove(self)
            bookmark.save()

class SharedPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts_shared")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="shares")
    quote = models.TextField(blank=True, null=True)
    date_shared = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_shared']

    def __str__(self):
          return '{}-shared-{}'.format(self.user.username, self.post.description)

    def get_model_type(self):
        return 'sharedpost'

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False, null=False)
    created = models.DateTimeField(auto_now_add=True)
    comment_likes = models.ManyToManyField(User,blank=True, related_name="comment_Likes")

    def like(self, account):
        if not account in self.comment_likes.all():
            self.comment_likes.add(account)

    def unlike(self, account):
        if account in self.comment_likes.all():
            self.comment_likes.remove(account)


    def __str__(self):
        return "{} comment, on {}".format(self.user.username, self.post.id)

class Bookmark(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = "bookmark")
    posts = models.ManyToManyField(Post,blank=True, related_name = "bookmarks")

    def __str__(self):
          return '{}-bookmark'.format(self.user.username)
