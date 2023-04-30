from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

# Adds email to default django user creation form
class UserRegisterForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['username']