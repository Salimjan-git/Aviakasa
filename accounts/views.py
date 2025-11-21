from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .models import CustomUser

def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')

    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
    confirm = request.POST.get('confirm_password')

    if not username or not email or not password:
        return render(request, 'register.html', {
            'username': username,
            'email': email,
            'error': 'All fields are required!'
        })

    if password != confirm:
        return render(request, 'register.html', {
            'username': username,
            'email': email,
            'error': 'Passwords do not match!'
        })

    if CustomUser.objects.filter(username=username).exists():
        return render(request, 'register.html', {
            'email': email,
            'error': 'Username already exists!'
        })

    if CustomUser.objects.filter(email=email).exists():
        return render(request, 'register.html', {
            'username': username,
            'error': 'Email already exists!'
        })

    user = CustomUser.objects.create_user(email=email, password=password, username=username)

    return redirect('login')


def login_view(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    email = request.POST.get('email')
    password = request.POST.get('password')

    if not email or not password:
        return render(request, 'login.html', {
            'email': email,
            'error': 'All fields are required!'
        })

    user = authenticate(request, email=email, password=password)
    if user is not None:
        login(request, user)
        return redirect('/')
    
    return render(request, 'login.html', {
        'email': email,
        'error': "Invalid email or password!"
    })


def logout_view(request):
    logout(request)
    return redirect('login')
