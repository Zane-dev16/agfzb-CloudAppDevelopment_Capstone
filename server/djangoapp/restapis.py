import requests
import json
# import related models here
from requests.auth import HTTPBasicAuth


def get_request(url, **kwargs):
    print(kwargs)
    print(f"GET from {url}")
    try:
        requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        response.raise_for_status()  # Raise exception for bad status codes (4xx or 5xx)
    except requests.exceptions.RequestException as e:
        print(f"Network exception occurred: {e}")
        return None
    
    status_code = response.status_code
    print(f"With status {status_code}")
    
    try:
        json_data = response.json()  # Try to parse JSON response
        return json_data
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
        return None

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)

def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url, **kwargs)  # Call get_request with the specified URL and kwargs
    
    if json_result:
        dealers = json_result.get("rows", [])  # Extract 'rows' from the JSON result or default to an empty list
        
        for dealer in dealers:
            dealer_doc = dealer.get("doc", {})  # Extract 'doc' from each dealer object or default to an empty dictionary
            
            # Create a CarDealer object with values from the 'doc' object
            dealer_obj = CarDealer(
                address=dealer_doc.get("address"),
                city=dealer_doc.get("city"),
                full_name=dealer_doc.get("full_name"),
                id=dealer_doc.get("id"),
                lat=dealer_doc.get("lat"),
                long=dealer_doc.get("long"),
                short_name=dealer_doc.get("short_name"),
                st=dealer_doc.get("st"),
                zip=dealer_doc.get("zip")
            )
            
            results.append(dealer_obj)  # Append the created CarDealer object to the results list
            
    
    return results  # Return the list of CarDealer objects

class DealerReview:
    def __init__(self, dealership, name, purchase, review, purchase_date, car_make, car_model, car_year, sentiment, id):
        self.dealership = dealership
        self.name = name
        self.purchase = purchase
        self.review = review
        self.purchase_date = purchase_date
        self.car_make = car_make
        self.car_model = car_model
        self.car_year = car_year
        self.sentiment = sentiment
        self.id = id

    def __str__(self):
        return f"Review ID: {self.id}, Dealer: {self.dealership}, Name: {self.name}, Sentiment: {self.sentiment}"

def get_dealer_reviews_from_cf(dealer_id):
    url = f"your-cloud-function-domain/reviews/review-get"  # Replace with your cloud function URL
    results = []
    
    # Call get_request with dealerId parameter to fetch reviews for the specified dealer ID
    json_result = get_request(url, dealerId=dealer_id)
    
    if json_result:
        reviews = json_result.get("reviews", [])  # Extract 'reviews' from the JSON result or default to an empty list
        
        for review in reviews:
            # Create a DealerReview object with values from the review object
            sentiment = analyze_review_sentiments(review.get("review"))
            dealer_review = DealerReview(
                dealership=review.get("dealership"),
                name=review.get("name"),
                purchase=review.get("purchase"),
                review=review.get("review"),
                purchase_date=review.get("purchase_date"),
                car_make=review.get("car_make"),
                car_model=review.get("car_model"),
                car_year=review.get("car_year"),
                sentiment=sentiment,
                id=review.get("id")
            )

            results.append(dealer_review)  # Append the created DealerReview object to the results list
    
    return results 

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        reviews = get_dealer_reviews_from_cf(dealer_id)
        context = {'reviews': reviews}
        return render(request, 'dealer_details.html', context)  # Assuming there's an HTML template for displaying reviews
    return HttpResponse("Invalid request method")

def analyze_review_sentiments(review_text):
    url = "your-watson-nlu-endpoint"  # Replace with your Watson NLU endpoint
    params = dict()
    params["text"] = kwargs["text"]
    params["version"] = kwargs["version"]
    params["features"] = kwargs["features"]
    params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                        auth=HTTPBasicAuth('apikey', api_key))
        
    if response:
        sentiment = response.get("sentiment", {}).get("document", {}).get("label")
        return sentiment
    
    return None

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



