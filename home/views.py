from django.shortcuts import render, redirect
from .models import User
from .forms import MyUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def home(request):
    return render(request, 'home/home.html', {})

def loginPage(request):
    page = "login"
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')


        try:
            user = User.objects.get(email=email)

        except:
            messages.error(request, 'User does not exist')


        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        else:
            messages.error(request, 'Username OR password does not exist')

    context = {'page': page}
    return render(request, "home/register.html",context)

def registerPage(request):
    form = MyUserCreationForm()

    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'home/register.html', {'form': form})

def logoutPage(request):
    logout(request)
    return redirect('home')

def profilePage(request, pk):
    user = User.objects.get(id=pk)

    return render(request, "home/profile.html", {"user": user})

def aboutPage(request):
    return render(request, "home/about.html", {})


