from django.shortcuts import render, redirect,HttpResponse
from .models import *


def home(request):
    if request.user.is_authenticated:
        flights = Flights.objects.all()
        return render(request, 'home.html', context={"flights": flights})
    else:
        return redirect('login')
    
    
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


