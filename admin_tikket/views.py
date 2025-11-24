from django.shortcuts import render, redirect, HttpResponse
from .models import *
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone


def home(request):
    if request.user.is_authenticated:
        flights = Flights.objects.all()
        return render(request, 'home.html', context={"flights": flights})
    else:
        return redirect('login')


def search_flights(request):
    if request.method == 'POST':
        departure = request.POST.get('departure')
        arrival = request.POST.get('arrival')
        date = request.POST.get('date')

        flights = Flights.objects.filter(
            Q(departure_airport__city__icontains=departure) |
            Q(departure_airport__name__icontains=departure) |
            Q(departure_airport__code__icontains=departure),
            Q(arrival_airport__city__icontains=arrival) |
            Q(arrival_airport__name__icontains=arrival) |
            Q(arrival_airport__code__icontains=arrival)
        )

        if date:
            flights = flights.filter(departure_time__date=date)

        return render(request, 'flights_list.html', {'flights': flights})

    return render(request, 'search.html')


def flight_detail(request, flight_id):
    try:
        flight = Flights.objects.get(id=flight_id)
        seats = Seat.objects.filter(aircraft=flight.aircraft_id)

        return render(request, 'flight_detail.html', {
            'flight': flight,
            'seats': seats
        })
    except Flights.DoesNotExist:
        return HttpResponse("Рейс не найден")


def flight_schedule(request):
    flights = Flights.objects.all().order_by('departure_time')
    return render(request, 'flight_schedule.html', {'flights': flights})


def user_profile(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему')
        return redirect('login')

    user_bookings = Booking.objects.filter(user=request.user).count()
    user_tickets = Ticket.objects.filter(booking__user=request.user).count()

    return render(request, 'user_profile.html', {
        'user_bookings': user_bookings,
        'user_tickets': user_tickets
    })


def book_flight(request, flight_id):
    try:
        flight = Flights.objects.get(id=flight_id)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                messages.error(request, 'Войдите в систему для бронирования')
                return redirect('login')

            passenger_name = request.POST.get('passenger_name')
            passport_number = request.POST.get('passport_number')
            seat_id = request.POST.get('seat_id')

            existing_ticket = Ticket.objects.filter(
                Q(flight=flight) &
                (Q(passenger_name=passenger_name) | Q(passport_number=passport_number))
            ).first()

            if existing_ticket:
                messages.error(request, 'Пассажир уже забронирован на этот рейс')
                return redirect('flight_detail', flight_id=flight_id)

            booking = Booking(
                user=request.user,
                total_price=flight.base_price,
                status='confirmed'
            )
            booking.save()

            
            ticket = Ticket(
                booking=booking,
                flight=flight,
                seat_id=seat_id,
                passenger_name=passenger_name,
                passport_number=passport_number,
                price=flight.base_price
            )
            ticket.save()

            messages.success(request, f'Билет забронирован! Номер: {ticket.id}')
            return redirect('my_bookings')

        seats = Seat.objects.filter(aircraft=flight.aircraft_id)
        return render(request, 'book_flight.html', {
            'flight': flight,
            'seats': seats
        })

    except Flights.DoesNotExist:
        return HttpResponse("Рейс не найден")
    
def find_cheapest_flights(request):
    departure = request.GET.get('departure', '')
    arrival = request.GET.get('arrival', '')

    if departure and arrival:
        cheapest_flights = Flights.objects.filter(
            Q(departure_airport__city__icontains=departure) &
            Q(arrival_airport__city__icontains=arrival)
        ).order_by('base_price')[:5]
    else:
        cheapest_flights = Flights.objects.all().order_by('base_price')[:10]

    if cheapest_flights:
        average_price = sum(flight.base_price for flight in cheapest_flights) // len(cheapest_flights)
    else:
        average_price = 0

    return render(request, 'cheapest_flights.html', {
        'cheapest_flights': cheapest_flights,
        'departure': departure,
        'arrival': arrival,
        'average_price': average_price
    })

def my_bookings(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему')
        return redirect('login')

    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')

    bookings = Booking.objects.filter(user=request.user)

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    if search_query:
        bookings = bookings.filter(
            Q(tickets__passenger_name__icontains=search_query) |
            Q(tickets__passport_number__icontains=search_query)
        ).distinct()

    return render(request, 'my_bookings.html', {
        'bookings': bookings,
        'status_filter': status_filter,
        'search_query': search_query
    })


def booking_detail(request, booking_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему')
        return redirect('login')

    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
        tickets = Ticket.objects.filter(booking=booking)

        return render(request, 'booking_detail.html', {
            'booking': booking,
            'tickets': tickets
        })
    except Booking.DoesNotExist:
        return HttpResponse("Бронирование не найдено")


def advanced_search(request):
    if request.method == 'POST':
        departure = request.POST.get('departure')
        arrival = request.POST.get('arrival')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        max_price = request.POST.get('max_price')
        airline = request.POST.get('airline')

        query = Q()

        if departure:
            query &= Q(departure_airport__city__icontains=departure) | Q(departure_airport__name__icontains=departure)

        if arrival:
            query &= Q(arrival_airport__city__icontains=arrival) | Q(arrival_airport__name__icontains=arrival)

        if date_from and date_to:
            query &= Q(departure_time__date__range=[date_from, date_to])

        if max_price:
            query &= Q(base_price__lte=max_price)

        if airline:
            query &= Q(airline_id__name__icontains=airline)

        flights = Flights.objects.filter(query).order_by('departure_time')

        return render(request, 'advanced_search_results.html', {'flights': flights})

    airlines = Airline.objects.all()
    return render(request, 'advanced_search.html', {'airlines': airlines})


def search_airports(request):
    query = request.GET.get('q', '')

    if query:
        airports = Airport.objects.filter(
            Q(name__icontains=query) |
            Q(city__icontains=query) |
            Q(country__icontains=query) |
            Q(code__icontains=query)
        )[:10]
    else:
        airports = []

    return render(request, 'airport_search.html', {
        'airports': airports,
        'query': query
    })


def admin_dashboard(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    total_flights = Flights.objects.count()
    active_bookings = Booking.objects.filter(~Q(status='cancelled')).count()
    cancelled_bookings = Booking.objects.filter(Q(status='cancelled')).count()
    completed_payments = Payment.objects.filter(Q(status='completed')).count()

    recent_bookings = Booking.objects.filter(~Q(status='cancelled')).order_by('-created_at')[:5]

    return render(request, 'admin/dashboard.html', {
        'total_flights': total_flights,
        'active_bookings': active_bookings,
        'cancelled_bookings': cancelled_bookings,
        'completed_payments': completed_payments,
        'recent_bookings': recent_bookings
    })


def admin_flight_search(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    airline_filter = request.GET.get('airline', '')
    airport_filter = request.GET.get('airport', '')
    date_filter = request.GET.get('date', '')

    flights = Flights.objects.all()

    if airline_filter:
        flights = flights.filter(Q(airline_id__name__icontains=airline_filter))

    if airport_filter:
        flights = flights.filter(
            Q(departure_airport__city__icontains=airport_filter) |
            Q(arrival_airport__city__icontains=airport_filter)
        )

    if date_filter:
        flights = flights.filter(Q(departure_time__date=date_filter))

    airlines = Airline.objects.all()

    return render(request, 'admin/flight_search.html', {
        'flights': flights,
        'airlines': airlines,
        'filters': {
            'airline': airline_filter,
            'airport': airport_filter,
            'date': date_filter
        }
    })


def admin_booking_search(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    passenger_name = request.GET.get('passenger_name', '')
    passport_number = request.GET.get('passport_number', '')
    status = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    bookings = Booking.objects.all()

    if passenger_name:
        bookings = bookings.filter(Q(tickets__passenger_name__icontains=passenger_name))

    if passport_number:
        bookings = bookings.filter(Q(tickets__passport_number__icontains=passport_number))

    if status:
        bookings = bookings.filter(Q(status=status))

    if date_from and date_to:
        bookings = bookings.filter(Q(created_at__date__range=[date_from, date_to]))
    elif date_from:
        bookings = bookings.filter(Q(created_at__date__gte=date_from))
    elif date_to:
        bookings = bookings.filter(Q(created_at__date__lte=date_to))

    return render(request, 'admin/booking_search.html', {'bookings': bookings})


def admin_revenue_analysis(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, 'Доступ запрещен')
        return redirect('home')

    period = request.GET.get('period', 'all')

    payments = Payment.objects.filter(Q(status='completed'))

    if period == 'today':
        payments = payments.filter(Q(paid_at__date=timezone.now().date()))

    total_revenue = sum(payment.amount for payment in payments)

    airline_revenue = {}
    for payment in payments:
        airline_name = payment.booking.tickets.first().flight.airline_id.name
        if airline_name not in airline_revenue:
            airline_revenue[airline_name] = 0
        airline_revenue[airline_name] += payment.amount

    return render(request, 'admin/revenue_analysis.html', {
        'total_revenue': total_revenue,
        'payments': payments,
        'airline_revenue': airline_revenue,
        'period': period
    })


def user_dashboard(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Войдите в систему')
        return redirect('login')

    active_bookings = Booking.objects.filter(
        Q(user=request.user) & ~Q(status='cancelled')
    ).count()

    upcoming_flights = Flights.objects.filter(
        Q(ticket__booking__user=request.user) &
        Q(ticket__booking__status='confirmed') &
        Q(departure_time__gte=timezone.now())
    ).distinct()

    flight_history = Flights.objects.filter(
        Q(ticket__booking__user=request.user) &
        Q(ticket__booking__status='confirmed') &
        Q(departure_time__lt=timezone.now())
    ).distinct()[:10]

    return render(request, 'user_dashboard.html', {
        'active_bookings': active_bookings,
        'upcoming_flights': upcoming_flights,
        'flight_history': flight_history
    })


def find_cheapest_flights(request):
    departure = request.GET.get('departure', '')
    arrival = request.GET.get('arrival', '')

    if departure and arrival:
        cheapest_flights = Flights.objects.filter(
            Q(departure_airport__city__icontains=departure) &
            Q(arrival_airport__city__icontains=arrival)
        ).order_by('base_price')[:5]
    else:
        cheapest_flights = Flights.objects.all().order_by('base_price')[:10]

    return render(request, 'cheapest_flights.html', {
        'cheapest_flights': cheapest_flights,
        'departure': departure,
        'arrival': arrival
    })

def advanced_search(request):
    if request.method == 'POST':
        departure = request.POST.get('departure')
        arrival = request.POST.get('arrival')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        max_price = request.POST.get('max_price')
        airline = request.POST.get('airline')
        seat_class = request.POST.get('seat_class')
        direct_only = request.POST.get('direct_only')

        query = Q()

        if departure:
            query &= Q(departure_airport__city__icontains=departure) | Q(departure_airport__name__icontains=departure)

        if arrival:
            query &= Q(arrival_airport__city__icontains=arrival) | Q(arrival_airport__name__icontains=arrival)

        if date_from and date_to:
            query &= Q(departure_time__date__range=[date_from, date_to])

        if max_price:
            query &= Q(base_price__lte=max_price)

        if airline:
            query &= Q(airline_id__name__icontains=airline)



        flights = Flights.objects.filter(query).order_by('departure_time')

        return render(request, 'advanced_search_results.html', {'flights': flights})

    airlines = Airline.objects.all()
    return render(request, 'advanced_search.html', {'airlines': airlines})

def flight_status(request):
    flight_number = request.GET.get('flight_number', '')
    airline_name = request.GET.get('airline', '')
    date = request.GET.get('date', '')

    flights = Flights.objects.all()

    if flight_number:
        flights = flights.filter(Q(flight_number__icontains=flight_number))

    if airline_name:
        flights = flights.filter(Q(airline_id__name__icontains=airline_name))

    if date:
        flights = flights.filter(Q(departure_time__date=date))

    return render(request, 'flight_status.html', {'flights': flights})


def available_flights_by_airline(request, airline_id):
    try:
        airline = Airline.objects.get(id=airline_id)
        flights = Flights.objects.filter(
            Q(airline_id=airline_id) &
            Q(departure_time__gte=timezone.now())
        ).order_by('departure_time')

        return render(request, 'airline_flights.html', {
            'airline': airline,
            'flights': flights
        })
    except Airline.DoesNotExist:
        return HttpResponse("Авиакомпания не найдена")


def available_seats_with_filters(request, flight_id):
    try:
        flight = Flights.objects.get(id=flight_id)

        seat_class = request.GET.get('class', '')

        seats_query = Q(aircraft=flight.aircraft_id)

        if seat_class:
            seats_query &= Q(seat_class=seat_class)

        all_seats = Seat.objects.filter(seats_query)

        booked_tickets = Ticket.objects.filter(Q(flight=flight))
        booked_seat_ids = [ticket.seat_id for ticket in booked_tickets]

        available_seats = [seat for seat in all_seats if seat.id not in booked_seat_ids]

        return render(request, 'available_seats_filtered.html', {
            'flight': flight,
            'available_seats': available_seats,
            'seat_class': seat_class,
            'total_seats': len(all_seats),
            'available_count': len(available_seats)
        })

    except Flights.DoesNotExist:
        return HttpResponse("Рейс не найден")
    
def flight_list_views(request):
    flights = Flights.objects.all().order_by('departure_time')
    return render(request, 'flight_list.html', {
        'flights': flights
    })

