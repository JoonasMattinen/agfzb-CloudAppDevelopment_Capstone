from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel, CarMake
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf,get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    return render(request, 'about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    return render(request, 'contact.html')

# Create a `login_request` view to handle sign in request
# djangoapp/views.py

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('psw')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Redirect to a specific page after successful login
            return redirect('djangoapp:index')  # Replace 'djangoapp:index' with your desired URL
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'djangoapp:index')



# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to index view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to index page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://n2majo02-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai//dealerships/get"
        dealerships = get_dealers_from_cf(url)
        context["dealership_list"] = dealerships
        print(context["dealership_list"])
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://n2majo02-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai//dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
        context["dealer"] = dealer
        
        review_url = "url: https://n2majo02-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(review_url, dealer_id=dealer_id)
        context["reviews"] = reviews
        print(reviews)
        context["dealer_id"] = dealer_id
        
    return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    context = {}
    dealer_url = "https://n2majo02-3000.theiadocker-1-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai//dealerships/get"
    dealer = get_dealer_by_id_from_cf(dealer_url, dealer_id=dealer_id)
    context["dealer"] = dealer
    
    if request.method == 'GET':
        # Get cars for the dealer
        cars = CarModel.objects.all()
        print(cars)
        context["cars"] = cars
        
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_id = request.POST["car"]
            car = CarModel.objects.get(pk=car_id)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["id"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.car_make.make_name
            payload["car_model"] = car.car_model
            payload["car_year"] = int(car.car_year)

            new_payload = {}
            new_payload["review"] = payload
            review_post_url =  "https://n2majo02-5000.theiadocker-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            post_request(review_post_url, new_payload, id=id)

        return redirect("djangoapp:dealer_details", id=id)

