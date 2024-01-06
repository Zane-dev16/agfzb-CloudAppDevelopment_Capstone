import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from .data import dealerships, reviewlist
def get_request(url, **kwargs):
    params = dict()
    params["text"] = kwargs["text"]
    params["version"] = kwargs["version"]
    params["features"] = kwargs["features"]
    params["return_analyzed_text"] = kwargs["return_analyzed_text"]
     
    try:
        if api_key:
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                        auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = request.get(url, params=params)
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
def post_request(url, json_payload, **kwargs):
    reviewlist.append(json_payload)

# e.g., response = requests.post(url, params=kwargs, json=payload)

def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = dealerships  # Call get_request with the specified URL and kwargs
    
    if json_result:
        dealers = json_result.get("dealerships", [])  # Extract 'rows' from the JSON result or default to an empty list
        
        for dealer in dealers:
            # Create a CarDealer object with values from the 'doc' object
            dealer_obj = CarDealer(
                address=dealer.get("address"),
                city=dealer.get("city"),
                full_name=dealer.get("full_name"),
                id=dealer.get("id"),
                lat=dealer.get("lat"),
                long=dealer.get("long"),
                short_name=dealer.get("short_name"),
                st=dealer.get("st"),
                zip=dealer.get("zip")
            )
            
            results.append(dealer_obj)  # Append the created CarDealer object to the results list
            
    
    return results  # Return the list of CarDealer objects

def get_dealer_reviews_from_cf(dealer_id):
    url = f"your-cloud-function-domain/reviews/review-get"  # Replace with your cloud function URL
    results = []
    
    # Call get_request with dealerId parameter to fetch reviews for the specified dealer ID
    json_result = [review for review in reviewlist if review.get('dealership') == dealer_id]
    
    if json_result:
        
        for review in json_result:
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
    url = 'https://sn-watson-sentiment-bert.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/SentimentPredict'
    myobj = { "raw_document": { "text": review_text } }
    header = {"grpc-metadata-mm-model-id": "sentiment_aggregated-bert-workflow_lang_multi_stock"}
    response = requests.post(url, json = myobj, headers=header)
    response_data = json.loads(response.text)
    label = response_data['documentSentiment']['label']
    
    return label

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative



