from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
# from .models import related models
from .models import CarModel, CarMake
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_by_id_from_cf,get_dealer_reviews_from_cf, analyze_review_sentiments,post_request
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
        url = "https://n2majo02-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        context['dealership_list'] = dealerships
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://n2majo02-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer

        review_url = "https://n2majo02-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/get_reviews"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)

        # Analyze sentiment for each review
        for review in reviews:
            sentiment = analyze_review_sentiments(review.review)
            review.sentiment = sentiment  # Update the sentiment attribute of the review

        context["reviews"] = reviews  # Pass the list of reviews directly, without serializing to JSON
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, id):
    if request.user.is_authenticated:
        if request.method == "GET":
            context = {}
    
            # Get cars for the dealer
            cars = CarModel.objects.all()
            print(cars)
            context["cars"] = cars

            dealer_url = "https://n2majo02-3000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/dealerships/get"
            dealer = get_dealer_by_id_from_cf(dealer_url, id=id)  

            context["dealer"] = dealer
            context["id"] = id

            return render(request, "djangoapp/add_review.html", context)

        if request.method == "POST":
            user = request.user
            review = {}
            review["id"] = id
            review["time"] = datetime.utcnow().isoformat()
            review["name"] = f"{user.first_name} {user.last_name}"
            review["dealership"] = id
            review["review"] = request.POST['content']
            checked = request.POST.get('purchasecheck', False)

            if checked == "on":
                checked = True
            review["purchase"] = checked
            review["purchase_date"] = request.POST['purchasedate']

            # Retrieve the selected car from the form
            selected_car_id = request.POST['car']
            selected_car = CarModel.objects.get(pk=selected_car_id)

            review["car_make"] = selected_car.make.name
            review["car_model"] = selected_car.name
            review["car_year"] = int(selected_car.year.strftime("%Y"))

            url = "https://n2majo02-5000.theiadocker-2-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/api/post_review"
            json_payload = {}
            json_payload["review"] = review
            post_request(url, json_payload, dealerId=id)
            print("Review submitted.")

            return redirect("djangoapp:dealer_details", id=id)
            
    else: 
        print("User is not authenticated")
        return redirect("djangoapp:dealer_details", id=id)

