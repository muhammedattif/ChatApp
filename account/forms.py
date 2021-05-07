from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from account.models import Account, get_default_profile_image
from django.conf import settings
class RegisterationForm(UserCreationForm):
    email = forms.EmailField(max_length=255, help_text="Required. Add a valid Email Address.")

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2')


    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        try:
            account = Account.objects.get(email = email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError("Account with this email is already in use.")


    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            account = Account.objects.get(username = username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError("Account with this username is already in use.")

class LoginForm(forms.ModelForm):

    # password = forms.CharField(label="Password", widget=forms.PasswordInput)
    #
    class Meta:
        model = Account
        fields = ('email', 'password')

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email = email, password = password):
                raise forms.ValidationError("Incorrect email or password")

class AccountUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('profile_img','username', 'email','first_name', 'last_name','bio', 'hide_email', 'is_private', 'active_status')


    def clean_email(self):
        email = self.cleaned_data['email'].lower()

        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(email = email)
        except Account.DoesNotExist:
            return email
        raise forms.ValidationError("Account with this email is already in use.")

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            account = Account.objects.exclude(pk=self.instance.pk).get(username = username)
        except Account.DoesNotExist:
            return username
        raise forms.ValidationError("Account with this username is already in use.")


    def clean_profile_img(self):
        image = self.cleaned_data.get('profile_img', False)
        if image:
            max_size = settings.DATA_UPLOAD_MAX_MEMORY_SIZE
            if image.size > max_size:
                raise forms.ValidationError("Profile image must has a file size less than {} MB".
                format(round(max_size/(1024*1024))))

        return image

    # def clean(self):
    #     self.cleaned_data = super(AccountUpdateForm, self).clean()
    #
    #     if not self.cleaned_data['profile_img']:
    #         self.cleaned_data['profile_img']= get_default_profile_image()
    #         self.instance.profile_img = get_default_profile_image()
    #
    #     return self.cleaned_data

    def save(self, commit=True):
        account = super(AccountUpdateForm, self).save(commit=False)
        account.profile_img = self.cleaned_data['profile_img']
        if not account.profile_img :
            account.profile_img = get_default_profile_image()
        account.username = self.cleaned_data['username']
        account.email = self.cleaned_data['email']
        account.hide_email = self.cleaned_data['hide_email']

        if commit:
            account.save()
        return account
