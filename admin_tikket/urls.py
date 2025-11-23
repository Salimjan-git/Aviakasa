from django.urls import path
from admin_tikket.views import home
from accounts.views import register_view, login_view, logout_views
from .views import *

urlpatterns = [
    path("", home, name='home'),
    path("register/", register_view, name='register'),
    path("login/", login_view, name='login'),
    path("logout/", logout_views, name='logout'),
    path('flight/',flight_list_views,name = 'flight_list'),
    path("search/",flight_search, name="flight_search"),
    # path("flights/results/",flight_results, name="flight_results"),
    # path("flights/<int:flight_id>/", flight_detail, name="flight_detail"),
    # path("booking/create/<int:flight_id>/",booking_create, name="booking_create"),
    # path("booking/<int:booking_id>/",booking_detail, name="booking_detail"),
    # path("payment/<int:booking_id>/",payment_page, name="payment_page"),
    # path("payment/confirm/<int:booking_id>/",payment_confirm, name="payment_confirm"),
]
