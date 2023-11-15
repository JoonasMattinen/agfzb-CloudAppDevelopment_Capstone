from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model 
class CarMake(models.Model):
    name = models.CharField(null=False, max_length=30)
    description = models.CharField(null=False, max_length=30)

    def __str__(self):
        return self.name + " " + self.description


# <HINT> Create a Car Model model 
class CarModel(models.Model):
    id = models.IntegerField(default=1,primary_key=True)
    name = models.CharField(null=False, max_length=100, default='Car')
   
    SEDAN = 'Sedan'
    SUV = 'SUV'
    WAGON = 'Wagon'
    MINIVAN = 'Minivan'
    CAR_TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, 'Wagon'),
        (MINIVAN, 'Minivan')
    ]

    type = models.CharField(
        null=False,
        max_length=50,
        choices=CAR_TYPES,
        default=SEDAN
    )
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    year = models.DateField(default=now)

    def __str__(self):
        return "Name: " + self.name

# <HINT> Create a plain Python class `CarDealer` to hold dealer data
class CarDealer:

    def __init__(self, address, city, id, lat, long, st, zip, full_name):
        # Dealer address
        self.address = address
        # Dealer city
        self.city = city
       
        # Dealer id
        self.id = id
        # Location lat
        self.lat = lat
        # Location long
        self.long = long

        # Dealer state
        self.st = st
        # Dealer zip
        self.zip = zip

        # Full name
        self.full_name = full_name

    def __str__(self):
        return "Dealer name: " + self.full_name

# <HINT> Create a plain Python class `DealerReview` to hold review data
