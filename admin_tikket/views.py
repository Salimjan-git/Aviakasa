from django.shortcuts import render, redirect
from .models import Aircraft,Airline,Airport,Flights
from django.contrib.auth.models import User


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return redirect('login')
    
    
def register_view(request):
    if request.method =='GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        pass