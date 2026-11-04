# places_api.py
# Talks to the Google Places API (New) using the requests library.

import requests
import pandas as pd

from settings import (PLACES_SEARCH_URL, FIELD_MASK, PAGE_SIZE, MAX_PAGES, TIMEOUT_SECONDS,
                      METERS_PER_MILE, CUISINES, PRICE_NAMES, PRICE_FROM_GOOGLE, SearchError)

COLUMNS = ["name", "cuisine", "address", "latitude", "longitude",
           "rating", "reviews", "price", "open_now", "maps_url"]


def request_page(api_key, body, http_post=requests.post):
    """Send one search request and return the decoded JSON.

    Every failure is turned into a SearchError with a clear message.
    http_post can be swapped out in tests so no real request is made.
    """
    headers = {"Content-Type": "application/json",
               "X-Goog-Api-Key": api_key,
               "X-Goog-FieldMask": FIELD_MASK}
    try:
        response = http_post(PLACES_SEARCH_URL, headers=headers, json=body,
                             timeout=TIMEOUT_SECONDS)
    except requests.Timeout:
        raise SearchError("Google took too long to respond. Please try again.")
    except requests.ConnectionError:
        raise SearchError("Couldn't connect to Google. Check your internet connection.")

    if response.status_code == 200:
        return response.json()

    # Google explains errors like {"error": {"status": "PERMISSION_DENIED", "message": "..."}}
    try:
        error = response.json().get("error", {})
    except ValueError:
        error = {}
    status = error.get("status", "")
    if response.status_code == 403 or status == "PERMISSION_DENIED":
        raise SearchError("Google rejected the API key. Check that Places API (New) is enabled, "
                          "billing is on, and the key is saved correctly.")
    if response.status_code == 429 or status == "RESOURCE_EXHAUSTED":
        raise SearchError("The daily request limit has been reached. Try again tomorrow.")
    if response.status_code == 400:
        raise SearchError("Google couldn't process that search: " + error.get("message", "bad request"))
    raise SearchError(f"Google returned an unexpected error (code {response.status_code}).")


def parse_place(place):
    """Turn one place from Google's response into a simple dictionary."""
    location = place.get("location", {})
    return {
        "name": place.get("displayName", {}).get("text", "Unknown"),
        "cuisine": place.get("primaryTypeDisplayName", {}).get("text", "Restaurant"),
        "address": place.get("formattedAddress", "Address not available"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "rating": place.get("rating"),
        "reviews": place.get("userRatingCount"),
        "price": PRICE_FROM_GOOGLE.get(place.get("priceLevel")),
        "open_now": place.get("currentOpeningHours", {}).get("openNow"),
        "maps_url": place.get("googleMapsUri", ""),
    }


def build_request_body(cuisine_choice, center, radius_miles, price_levels, min_rating, open_now):
    """Build the search request Google expects."""
    body = {
        "textQuery": CUISINES[cuisine_choice][0],
        "pageSize": PAGE_SIZE,
        "locationBias": {"circle": {
            "center": {"latitude": center[0], "longitude": center[1]},
            "radius": radius_miles * METERS_PER_MILE,
        }},
    }
    if price_levels:
        body["priceLevels"] = [PRICE_NAMES[level] for level in sorted(price_levels)]
    if min_rating > 0:
        body["minRating"] = min_rating
    if open_now:
        body["openNow"] = True
    return body


def fetch_places(api_key, body, http_post=requests.post):
    """Get up to MAX_PAGES pages of results.

    Returns (table, number_of_requests_made).
    """
    places = []
    calls = 0
    body = dict(body)
    for page in range(MAX_PAGES):
        data = request_page(api_key, body, http_post)
        calls += 1
        places += [parse_place(p) for p in data.get("places", [])]
        token = data.get("nextPageToken")
        if not token:
            break
        body["pageToken"] = token

    table = pd.DataFrame(places, columns=COLUMNS)
    table = table.dropna(subset=["latitude", "longitude"])
    return table, calls
