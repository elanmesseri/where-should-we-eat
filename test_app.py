# test_app.py
# Automated tests. Run with:  python test_app.py
# Uses fake Google responses, so it never uses real API requests.

from settings import NEIGHBORHOODS, SearchError
from places_api import build_request_body, fetch_places, request_page
from sample_data import load_sample_data
from filters import (distance_miles, filter_restaurants, sort_results, pick_random,
                     validate_inputs, price_text, rating_text)


def check(description, condition):
    print(("PASS  " if condition else "FAIL  ") + description)
    return condition


class FakeResponse:
    """Pretends to be a reply from Google."""
    def __init__(self, status_code, data):
        self.status_code = status_code
        self._data = data

    def json(self):
        return self._data


def fake_place(name, lat, lon, rating, reviews, price, open_now=True):
    return {"displayName": {"text": name}, "formattedAddress": "1 Test St, Miami, FL",
            "location": {"latitude": lat, "longitude": lon}, "rating": rating,
            "userRatingCount": reviews, "priceLevel": price,
            "primaryTypeDisplayName": {"text": "Cuban Restaurant"},
            "currentOpeningHours": {"openNow": open_now}, "googleMapsUri": "https://maps.google.com/?cid=1"}


PAGE1 = {"places": [fake_place("Close Cafe", 25.7660, -80.2190, 4.6, 900, "PRICE_LEVEL_INEXPENSIVE"),
                    fake_place("Pricey Spot", 25.7670, -80.2200, 4.2, 300, "PRICE_LEVEL_EXPENSIVE", False)],
         "nextPageToken": "abc"}
PAGE2 = {"places": [fake_place("Far Away Diner", 25.9000, -80.1300, 4.9, 50, "PRICE_LEVEL_MODERATE")]}
sent = []


def fake_post(url, headers, json, timeout):
    sent.append(dict(json))
    return FakeResponse(200, PAGE2 if "pageToken" in json else PAGE1)


def run_tests():
    results = []
    center = NEIGHBORHOODS["Little Havana"]

    # Google requests
    body = build_request_body("Cuban", center, 1.0, [1, 2], 4.5, True)
    results.append(check("request includes price, rating, and open now filters",
                         body["priceLevels"] == ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE"]
                         and body["minRating"] == 4.5 and body["openNow"] is True))
    df, calls = fetch_places("FAKE", build_request_body("Cuban", center, 1.0, [], 0, False), fake_post)
    results.append(check("follows the next page token (2 requests)", calls == 2 and sent[1]["pageToken"] == "abc"))
    results.append(check("Google price names become 1 to 4", list(df["price"]) == [1, 3, 2]))

    filtered = filter_restaurants(df, center, 1.0, "Cuban", [], 0, False, sample_mode=False)
    results.append(check("places outside the radius are removed", "Far Away Diner" not in list(filtered["name"])))
    results.append(check("best rated sort", list(sort_results(filtered, "Best rated")["name"]) == ["Close Cafe", "Pricey Spot"]))
    results.append(check("open now filter", list(filter_restaurants(df, center, 1.0, "Cuban", [], 0, True, False)["name"]) == ["Close Cafe"]))

    try:
        request_page("BAD", {}, lambda *a, **k: FakeResponse(403, {"error": {"status": "PERMISSION_DENIED"}}))
        results.append(check("rejected key shows a clear error", False))
    except SearchError as e:
        results.append(check("rejected key shows a clear error", "rejected" in str(e)))

    # Sample data
    sample = load_sample_data()
    cheap_cuban = filter_restaurants(sample, center, 1.0, "Cuban", [1, 2], 4.5, False, sample_mode=True)
    results.append(check(f"sample mode: cheap Cuban 4.5+ near Little Havana ({len(cheap_cuban)} found)",
                         len(cheap_cuban) > 0 and (cheap_cuban["price"] <= 2).all()
                         and (cheap_cuban["rating"] >= 4.5).all()))

    # Helpers and bad input
    d = distance_miles(*NEIGHBORHOODS["University of Miami"], *NEIGHBORHOODS["Brickell"])
    results.append(check(f"UM to Brickell is about 6 miles (got {d:.2f})", 5.5 < d < 6.5))
    results.append(check("price and rating text", price_text(3) == "$$$" and rating_text(4.56, 1200) == "4.6 ★ (1,200 reviews)"))
    try:
        validate_inputs("Narnia", 1.0, "Any", [])
        results.append(check("unknown neighborhood is rejected", False))
    except SearchError:
        results.append(check("unknown neighborhood is rejected", True))
    results.append(check("pick_random returns one of the results", pick_random(cheap_cuban)["name"] in list(cheap_cuban["name"])))
    try:
        pick_random(cheap_cuban.iloc[0:0])
        results.append(check("pick_random on no results raises an error", False))
    except SearchError:
        results.append(check("pick_random on no results raises an error", True))

    print(f"\n{sum(results)} of {len(results)} tests passed.")


if __name__ == "__main__":
    run_tests()
