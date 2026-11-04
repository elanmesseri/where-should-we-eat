# filters.py
# Distance, filtering, sorting, and the Pick for Me button.

import math
import random

import pandas as pd

from settings import CUISINES, NEIGHBORHOODS, PRICE_NAMES, SearchError


def distance_miles(lat1, lon1, lat2, lon2):
    """Straight line distance between two points on Earth (haversine formula)."""
    earth_radius_miles = 3958.8
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    a = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * earth_radius_miles * math.asin(math.sqrt(a))


def parse_min_rating(choice):
    """Convert the rating dropdown value to a number. "Any" means 0."""
    return 0.0 if choice == "Any" else float(choice)


def validate_inputs(neighborhood, radius_miles, cuisine_choice, price_levels):
    if neighborhood not in NEIGHBORHOODS:
        raise SearchError("Please choose a neighborhood from the list.")
    if cuisine_choice not in CUISINES:
        raise SearchError("Please choose a cuisine from the list.")
    if not 0.25 <= radius_miles <= 5:
        raise SearchError("Radius must be between 0.25 and 5 miles.")
    if any(level not in PRICE_NAMES for level in price_levels):
        raise SearchError("Price levels must be between $ and $$$$.")


def filter_restaurants(df, center, radius_miles, cuisine_choice, price_levels,
                       min_rating, open_now, sample_mode):
    """Apply every filter. Google already filters live results, but we check again
    so sample mode works the same way and nothing slips through."""
    df = df.copy()
    df["distance"] = [round(distance_miles(center[0], center[1], lat, lon), 2)
                      for lat, lon in zip(df["latitude"], df["longitude"])]
    df = df[df["distance"] <= radius_miles]   # Google's circle is a preference, not a hard limit

    if sample_mode and CUISINES[cuisine_choice][1]:
        df = df[df["cuisine"].isin(CUISINES[cuisine_choice][1])]
    if price_levels:
        df = df[df["price"].isin(price_levels)]
    if min_rating > 0:
        df = df[df["rating"].fillna(0) >= min_rating]
    if open_now:
        df = df[df["open_now"] == True]
    return df.reset_index(drop=True)


def sort_results(df, sort_choice):
    if sort_choice == "Best rated":
        df = df.sort_values(["rating", "reviews"], ascending=False, na_position="last")
    elif sort_choice == "Most reviews":
        df = df.sort_values("reviews", ascending=False, na_position="last")
    elif sort_choice == "Lowest price":
        df = df.sort_values("price", ascending=True, na_position="last")
    elif sort_choice == "Highest price":
        df = df.sort_values("price", ascending=False, na_position="last")
    else:
        df = df.sort_values("distance")
    return df.reset_index(drop=True)


def pick_random(df):
    """Choose one restaurant at random. Raises SearchError if there are none."""
    if len(df) == 0:
        raise SearchError("There are no restaurants to pick from. Try loosening your filters.")
    return df.iloc[random.randint(0, len(df) - 1)]


def price_text(price):
    return "$" * int(price) if pd.notna(price) else "N/A"


def rating_text(rating, reviews=None):
    if pd.isna(rating):
        return "No rating"
    text = f"{rating:.1f} ★"
    if reviews is not None and pd.notna(reviews):
        text += f" ({int(reviews):,} reviews)"
    return text
