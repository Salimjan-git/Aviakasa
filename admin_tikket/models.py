from django.db import models
from django.conf import settings

class Airport(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=200,unique=True)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f'{self.code}'
    
    
class Airline(models.Model):
    name = models.CharField(max_length=100)
    code = models.IntegerField()
    logo = models.ImageField()
    
    def __str__(self):
        return f'{self.name}'
    

class Aircraft(models.Model):
    model_plane = models.CharField(max_length=100)
    seat_count = models.IntegerField()
    
    def __str__(self):
        return f"{self.model_plane}"
    

class Flights(models.Model):
    airline_id = models.ForeignKey(Airline,on_delete=models.CASCADE)
    aircraft_id = models.ForeignKey(Aircraft,on_delete=models.CASCADE)
    flight_number = models.IntegerField()
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE ,related_name='departures')
    arrival_airport = models.ForeignKey(Airport , on_delete=models.CASCADE ,related_name='arrivals')
    departure_time = models.DateTimeField(auto_now_add=True)
    arrival_time = models.DateTimeField(auto_now_add=True)
    base_price = models.IntegerField()
    

    
class Seat(models.Model):
    aircraft = models.ForeignKey(Aircraft,on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=100)
    seat_class = models.CharField(max_length=100)
    
    
class Ticket(models.Model):
    flight = models.ForeignKey(Flights,on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat,on_delete=models.CASCADE)
    passenger_name = models.CharField( max_length=100)
    passport_number = models.CharField(max_length=100)
    price = models.IntegerField()
    

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.CASCADE ,related_name='booking')
    
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=100)
    

class Payment(models.Model):
    booking = models.OneToOneField(Booking,on_delete=models.CASCADE)
    amount = models.IntegerField()
    payment_method = models.CharField(max_length=100)
    status = models.CharField(max_length=200)
    paid_at = models.BooleanField(default=False)
    
