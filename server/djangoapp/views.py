from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
# from .restapis import related methods
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)


def login_request(request):
    context = {}
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['password']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
    return redirect('djangoapp:index')


def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

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
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "your-cloud-function-domain/dealerships/dealer-get"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        
        context['dealerships'] = dealerships
        # Render the template with dealerships in the context
        return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {
            "reviews": get_dealer_reviews_from_cf(dealer_id), 
            "dealer_id": dealer_id
        }
        return render(request, 'djangoapp/dealer_details.html', context)
    return HttpResponse("Invalid request method")


id = 100
def add_review(request, dealer_id):
    cars = CarModel.objects.filter(dealer_id=dealer_id)
    context = {"dealer_id": dealer_id, "cars": cars}

    if request.method == "GET":
        return render(request, "djangoapp/add_review.html", context)
    if request.method == "POST":
        global id
        id += 1
        review = {
            "id": id,
            "name": "John Doe",
            "dealership": dealer_id,
            "review": request.POST.get("content"),
            "purchase": "purchasecheck" in request.POST,
            "purchase_date": request.POST.get("purchasedate"),
            "car_make": CarModel.objects.get(id=request.POST.get("car")).car_make.name,
            "car_model": CarModel.objects.get(id=request.POST.get("car")).name,
            "car_year": CarModel.objects.get(id=request.POST.get("car")).year.strftime("%Y"),
            "time": datetime.utcnow().isoformat(),
        }
        
        # Assuming you have a function to post the review to a URL/API
        # Replace "random url" with your actual endpoint
        post_request("random url", review)
        
        # Redirect to the dealer details page
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)