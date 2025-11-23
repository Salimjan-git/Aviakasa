from django.shortcuts import render, redirect,HttpResponse
from .models import *
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return redirect('login')
    
    
def register_view(request):
    if request.method =='GET':
        return render(request, 'register.html')
    elif request.method == 'POST':
        username =  request.POST.get('username' ,None)
        email = request.POST.get('email',None)
        password = request.POST.get('password',None)
        confirm = request.POST.get('confirm', None)
        
        if not username or not email or not password :
            return render(request,'register.html' ,context={
                'username': username,
                'email' : email,
                'error' : 'Fields are required'
            })
            
        if password != confirm :
            return render(request,'register.html' ,context={
                'username': username,
                'email' : email,
                'error' : 'Password do not match'
            })
        
        hash_password = make_password(password)
        user = User(
            username = username,
            email = email,
            password = hash_password)
        user.save()
        return redirect('/')
        
        
def login_view(request):
    if request.method =='GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username =  request.POST.get('username' ,None)
        password = request.POST.get('password',None)
        if not username  or not password :
            return render(request,'login.html' ,context={
                'username': username,
                'error' : 'Username must be set'
            })
        
        user = authenticate(request,
            username = username,
            password = password
        )
        if user :
            login(request , user)
        return redirect('/')

def logout_views(request):
    try:
        logout(request)
        return redirect('login')
    except Exception as err:
        return HttpResponse(str(err))
    
    
def flight_list_views(request):
    flight = Flights.objects.all()
    return render(request , 'flight_list.html',
                context={'flight':flight})
    
def flight_search(request):
    departure = request.GET.get("departure")
    arrival = request.GET.get("arrival")

    flights = Flights.objects.filter(
        departure_airport__name__icontains=departure,
        arrival_airport__name__icontains=arrival
    )

    return render(request, "flight_search_results.html", {"flights": flights})


