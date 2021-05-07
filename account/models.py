from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from posts.models import Post, SharedPost
from django.db.models import Q

def get_profile_image_filepath(self, filename):
    return f'profile_images/{self.pk}/{"profile_image.png"}'

def get_default_profile_image():
    return 'imgs/profile_image.png'

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("Users must have an Email Address")
        if not username:
            raise ValueError("Users must have a Username")
        user = self.model(
            email = self.normalize_email(email),
            username = username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=60, unique=True)
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(blank=True, null=True,max_length=30, default='')
    last_name = models.CharField(blank=True, null=True,max_length=30, default='')
    bio = models.TextField(blank=True, null=True,max_length=100, default='')
    date_joined = models.DateTimeField(verbose_name="Date Joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="Last Login", auto_now=True)
    profile_img = models.ImageField(max_length=255, upload_to=get_profile_image_filepath, null=True, blank=True, default=get_default_profile_image)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    hide_email = models.BooleanField(verbose_name="Hide Email", default=True)
    is_private = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    active_status = models.BooleanField(default=True)

    objects = MyAccountManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    #delete the image if new one is set
    def save(self, *args, **kwargs):
        # delete old images when replacing by updating the image
        try:
            this = Account.objects.get(id=self.id)

            # if the default image, don't delete it
            if this.profile_img != self.profile_img:
                if 'imgs/'not in this.profile_img.url:
                    this.profile_img.delete(save=False)
        except: pass # when new image then we do nothing, normal case
        super(Account, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    def get_online_status(self):
        if self.active_status:
            if self.is_online:
                return True
        return False

    def get_profile_url(self):
        return "/account/{}".format(self.id)

    def get_profile_image_filename(self):
        return str(self.profile_image)[str(self.profile_image).index(f'profile_images/{self.pk}/'):]

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def has_module_perms(self, app_label):
        return True

    def get_news_feed(self):
        posts = []
        friends_ids = self.friends.values_list("user__id", flat=True)
        friends_own_posts = Post.objects.filter(user__id__in = friends_ids ).exclude(privacy = 'private')
        friends_shared_posts = SharedPost.objects.filter(user__id__in = friends_ids).exclude(~Q(post__user__id__in = friends_ids))
        posts.append(friends_own_posts)
        posts.append(friends_shared_posts)
        return posts
