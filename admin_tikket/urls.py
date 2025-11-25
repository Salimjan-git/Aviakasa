from django.urls import path
from admin_tikket.views import home
from accounts.views import register_view, login_view, logout_views
from .views import (
    flight_list_views,
    search_flights,
    advanced_search,
    flight_detail,
    book_flight,
    my_bookings,
    booking_detail,
    search_airports,
    find_cheapest_flights,
    flight_status,
    flight_schedule,
    available_flights_by_airline,
    user_dashboard,
    available_seats_with_filters,
    admin_dashboard,
    admin_flight_search,
    admin_booking_search,
    admin_revenue_analysis,
    user_profile,
)


urlpatterns = [
    
    path("", home, name='home'),
    path("register/", register_view, name='register'),
    path("login/", login_view, name='login'),
    path("logout/", logout_views, name='logout'),
    path("flight/", flight_list_views, name='flight_list'),
    path("search/", search_flights, name="search_flights"),
    path("advanced-search/", advanced_search, name="advanced_search"),
    path("flight/<int:flight_id>/", flight_detail, name="flight_detail"),
    path("book/<int:flight_id>/", book_flight, name="book_flight"),
    path("schedule/", flight_schedule, name="flight_schedule"),
    path("seats/<int:flight_id>/", available_seats_with_filters, name="available_seats"),
    path("flight-status/", flight_status, name="flight_status"),
    path("cheapest-flights/", find_cheapest_flights, name="cheapest_flights"),
    path("search-airports/", search_airports, name="search_airports"),
    path("profile/", user_profile, name="user_profile"),
    path("dashboard/", user_dashboard, name="user_dashboard"),
    path("my-bookings/", my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/", booking_detail, name="booking_detail"),
    path("airline-flights/<int:airline_id>/", available_flights_by_airline, name="airline_flights"),
    path("admin/", admin_dashboard, name="admin_dashboard"),
    path("admin/flights/search/", admin_flight_search, name="admin_flight_search"),
    path("admin/bookings/search/", admin_booking_search, name="admin_booking_search"),
    path("admin/revenue/", admin_revenue_analysis, name="admin_revenue_analysis"),
]
