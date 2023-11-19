import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions
import time
 

def analyze_review_sentiments(dealer_review):
    api_key = "OVjNiyfnfKGbpQ5RpP5cTZw_AvJkuCEs6feGCPiivW7E"
    url = "https://api.eu-de.natural-language-understanding.watson.cloud.ibm.com/instances/9043cccb-0e4b-483d-8b6b-f389506ac79e"
    texttoanalyze= dealer_review
    version = '2020-08-01'
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2020-08-01',
    authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        text=dealer_review,
        language='en',
        features= Features(sentiment= SentimentOptions())
    ).get_result()
    print(json.dumps(response))
    sentiment_score = str(response["sentiment"]["document"]["score"])
    sentiment_label = response["sentiment"]["document"]["label"]
    print(sentiment_score)
    print(sentiment_label)
    sentiment = sentiment_label
    
    return sentiment


def get_dealers_from_cf(url, **kwargs):
    results = []
    state = kwargs.get("state")
    if state:
        json_result = get_request(url, state=state)
    else:
        json_result = get_request(url)

    # print('json_result from line 31', json_result)    

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            print(dealer_doc)
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"],
                                   dealer_id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"], full_name=dealer_doc["full_name"],
                                
                                   st=dealer_doc["st"], zip=dealer_doc["zip"],short_name=dealer_doc["short_name"],)
            results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    dealer_id = kwargs.get("dealer_id")
    # print("DEALER_ID ------------------->>>>>>>",dealer_id)
    if dealer_id:
        json_result = get_request(url, dealer_id=dealer_id)
    else:
        json_result = get_request(url)
    # print(json_result)
    # print("############################################")
    if json_result:
        print("LINE 67 --------->>>>>>>>", json_result)
        reviews = json_result
        for dealer_review in reviews:
            print(dealer_review)
            review_obj = DealerReview(
                name=dealer_review.get("name"),
                dealer_id=dealer_review.get("dealer_id"),
                review_id=dealer_review.get("review_id"), #reviewer id
                review=dealer_review.get("review"),
                purchase=dealer_review.get("purchase"),
                purchase_date=dealer_review.get("purchase_date"),
                car_make=dealer_review.get("car_make"),
                car_model=dealer_review.get("car_model"),
                car_year=dealer_review.get("car_year"),
                sentiment='',
            )
            print("REVIEWER ID------------>", dealer_review.get("id"))
            sentiment = analyze_review_sentiments(review_obj.review)
            print(sentiment)
            review_obj.sentiment = sentiment
            results.append(review_obj)
    return results

def get_dealer_by_id_from_cf(url, dealer_id):
    results = []

    # Call get_request with a URL parameter
    json_result = get_request(url, dealer_id=dealer_id)

    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        print("LINE 106---------->>>>>>>>>", dealers)
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            dealer_doc = dealer
            if dealer_doc["id"] == dealer_id:
                # Create a CarDealer object with values in `doc` object
                dealer_obj = CarDealer(address=dealer_doc["address"], 
                                       city=dealer_doc["city"], 
                                       full_name=dealer_doc["full_name"],
                                       dealer_id=dealer_doc["id"], 
                                       lat=dealer_doc["lat"], 
                                       long=dealer_doc["long"],
                                       short_name=dealer_doc["short_name"],
                                       st=dealer_doc["st"], 
                                       zip=dealer_doc["zip"])                    
                results.append(dealer_obj)

    return results[0]


def get_request(url, **kwargs):
    
    # If argument contain API KEY
    api_key = kwargs.get("api_key")
    print("GET from {} ".format(url))
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
            # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")

    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data



def post_request(url, payload, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    print(payload)
    response = requests.post(url, params=kwargs, json=payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


