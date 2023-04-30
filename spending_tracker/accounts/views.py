from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from accounts.forms import UserRegisterForm, UserUpdateForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('accounts:login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def guest_login(request):
    if request.method == 'POST':
        username= "guest"
        password= "Sn55MRG8!"

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            return redirect("accounts:profile")

    return redirect("accounts:login")

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)

        if request.user.username == "guest":
            messages.warning(request, f'Can not change guest username')
            return redirect('accounts:profile')

        if form.is_valid():
            form.save()
            messages.success(request, f'Profile has been updated!')
            return redirect('accounts:profile')

    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'accounts/profile.html', {'form': form})

@login_required
def deactivate_account(request):
    if request.user.username == "guest":
        messages.warning(request, f'Can not deactivate guest')
        return redirect('accounts:profile')
    
    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    return redirect('accounts:login')