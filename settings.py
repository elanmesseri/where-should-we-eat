# settings.py
# Shared settings: neighborhoods, cuisines, price names, and limits.

PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Only ask Google for the fields we use. Fewer fields keeps requests in a cheaper billing tier.
FIELD_MASK = ",".join([
    "places.displayName",
    "places.formattedAddress",
    "places.location",
    "places.rating",
    "places.userRatingCount",
    "places.priceLevel",
    "places.primaryTypeDisplayName",
    "places.currentOpeningHours.openNow",
    "places.googleMapsUri",
    "nextPageToken",
])

PAGE_SIZE = 20              # Google's maximum results per request
MAX_PAGES = 2               # at most 2 requests (40 results) per search
MAX_CALLS_PER_SESSION = 60  # safety limit so a bug can't run up a bill
TIMEOUT_SECONDS = 15
METERS_PER_MILE = 1609.34

# Center point (latitude, longitude) of each Miami area the user can search
NEIGHBORHOODS = {
    "University of Miami": (25.7215, -80.2793),
    "Brickell": (25.7617, -80.1918),
    "Downtown Miami": (25.7743, -80.1937),
    "Wynwood": (25.8010, -80.1990),
    "Design District": (25.8130, -80.1930),
    "Midtown": (25.8080, -80.1930),
    "MiMo and Little River": (25.8400, -80.1850),
    "South Beach": (25.7826, -80.1341),
    "Little Havana": (25.7656, -80.2198),
    "Coral Gables": (25.7493, -80.2635),
    "Coconut Grove": (25.7280, -80.2430),
    "South Miami": (25.7079, -80.2934),
}

# Cuisine in the dropdown -> (words sent to Google, matching categories in the sample data)
CUISINES = {
    "Any": ("restaurants", []),
    "American": ("American restaurant", ["American", "Southern"]),
    "Burgers": ("burger restaurant", ["Burgers"]),
    "Pizza": ("pizza restaurant", ["Pizza"]),
    "Italian": ("Italian restaurant", ["Italian"]),
    "Cuban": ("Cuban restaurant", ["Cuban"]),
    "Latin American": ("Latin American restaurant", ["Latin", "Argentinian"]),
    "Mexican": ("Mexican restaurant", ["Mexican"]),
    "Peruvian": ("Peruvian restaurant", ["Peruvian"]),
    "Japanese": ("Japanese restaurant", ["Japanese"]),
    "Sushi": ("sushi restaurant", ["Japanese"]),
    "Chinese": ("Chinese restaurant", ["Chinese"]),
    "Asian (other)": ("Asian restaurant", ["Asian", "Vietnamese"]),
    "Indian": ("Indian restaurant", ["Indian"]),
    "Mediterranean": ("Mediterranean restaurant", ["Mediterranean", "Greek"]),
    "Seafood": ("seafood restaurant", ["Seafood"]),
    "Steakhouse": ("steakhouse", ["Steakhouse"]),
    "BBQ": ("barbecue restaurant", ["BBQ"]),
    "Cafe and bakery": ("cafe bakery", ["Cafe", "Bakery", "Dessert", "Juice and Smoothies"]),
}

# Google's price names <-> our 1 to 4 scale
PRICE_NAMES = {
    1: "PRICE_LEVEL_INEXPENSIVE",
    2: "PRICE_LEVEL_MODERATE",
    3: "PRICE_LEVEL_EXPENSIVE",
    4: "PRICE_LEVEL_VERY_EXPENSIVE",
}
PRICE_FROM_GOOGLE = {name: level for level, name in PRICE_NAMES.items()}

RATING_CHOICES = ["Any", "3.5", "4.0", "4.3", "4.5", "4.7"]
SORT_CHOICES = ["Best rated", "Most reviews", "Closest", "Lowest price", "Highest price"]


class SearchError(Exception):
    """Raised with a message that is safe to show directly to the user."""
