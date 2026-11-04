# sample_data.py
# Real Miami restaurants used when no Google API key is set, so the app always works.
# Ratings, prices, and pin locations are APPROXIMATE and were entered by the team.

import urllib.parse
import pandas as pd

SAMPLE_RESTAURANTS = [
    # (name, neighborhood, cuisine, price 1 to 4, rating, latitude, longitude)
    ('Komodo', 'Brickell', 'Asian', 4, 4.3, 25.75959, -80.19599),
    ('Sexy Fish Miami', 'Brickell', 'Asian', 4, 4.4, 25.76351, -80.19693),
    ('La Mar by Gaston Acurio', 'Brickell', 'Peruvian', 4, 4.5, 25.76213, -80.19341),
    ("Truluck's", 'Brickell', 'Seafood', 4, 4.6, 25.7564, -80.19171),
    ('Baires Grill', 'Brickell', 'Argentinian', 3, 4.4, 25.75615, -80.1926),
    ('Hutong', 'Brickell', 'Chinese', 4, 4.5, 25.75654, -80.19671),
    ('CVI.CHE 105', 'Downtown', 'Peruvian', 2, 4.5, 25.77339, -80.18978),
    ('Toro Toro', 'Downtown', 'Latin', 3, 4.5, 25.76979, -80.19702),
    ('Novikov', 'Downtown', 'Asian', 4, 4.5, 25.77583, -80.18833),
    ('Zuma', 'Downtown', 'Japanese', 4, 4.6, 25.77523, -80.19494),
    ("Fooq's", 'Downtown', 'Mediterranean', 3, 4.6, 25.78002, -80.19914),
    ("Garcia's Seafood Grille", 'Downtown', 'Seafood', 2, 4.5, 25.7786, -80.19622),
    ('KYU', 'Wynwood', 'Asian', 3, 4.6, 25.79673, -80.20359),
    ('Coyo Taco', 'Wynwood', 'Mexican', 2, 4.5, 25.7987, -80.19521),
    ('1-800-Lucky', 'Wynwood', 'Asian', 2, 4.4, 25.79717, -80.19802),
    ('Zak the Baker', 'Wynwood', 'Bakery', 1, 4.6, 25.80267, -80.20053),
    ('Uchi Miami', 'Wynwood', 'Japanese', 4, 4.7, 25.80157, -80.20425),
    ('Wynwood Kitchen and Bar', 'Wynwood', 'Latin', 3, 4.3, 25.79572, -80.20253),
    ('Panther Coffee', 'Wynwood', 'Cafe', 1, 4.6, 25.80316, -80.19987),
    ('Doya', 'Wynwood', 'Mediterranean', 3, 4.7, 25.79877, -80.19797),
    ('Cote Miami', 'Design District', 'Steakhouse', 4, 4.7, 25.81244, -80.1954),
    ("Michael's Genuine", 'Design District', 'American', 3, 4.5, 25.81653, -80.19061),
    ('Mandolin Aegean Bistro', 'Design District', 'Greek', 3, 4.6, 25.80993, -80.19211),
    ('Ghee Indian Kitchen', 'Design District', 'Indian', 3, 4.6, 25.8133, -80.1885),
    ('Le Jardinier', 'Design District', 'French', 4, 4.6, 25.81575, -80.19554),
    ('Sugarcane Raw Bar Grill', 'Midtown', 'Latin', 3, 4.5, 25.81376, -80.19758),
    ('Phuc Yea', 'MiMo and Little River', 'Vietnamese', 3, 4.5, 25.83902, -80.18191),
    ('Blue Collar', 'MiMo and Little River', 'American', 2, 4.6, 25.83582, -80.18513),
    ('Boia De', 'MiMo and Little River', 'Italian', 3, 4.7, 25.83447, -80.18298),
    ('Versailles', 'Little Havana', 'Cuban', 2, 4.4, 25.76877, -80.21892),
    ('Ball and Chain', 'Little Havana', 'Cuban', 2, 4.5, 25.77011, -80.22204),
    ('El Rey de las Fritas', 'Little Havana', 'Cuban', 1, 4.4, 25.76794, -80.21867),
    ('Azucar Ice Cream', 'Little Havana', 'Dessert', 1, 4.7, 25.76656, -80.22033),
    ('Sanguich de Miami', 'Little Havana', 'Cuban', 1, 4.7, 25.76968, -80.21446),
    ('Doce Provisions', 'Little Havana', 'Latin', 2, 4.6, 25.76529, -80.21783),
    ('Cafe La Trova', 'Little Havana', 'Cuban', 3, 4.6, 25.76033, -80.21738),
    ('Los Pinarenos Fruteria', 'Little Havana', 'Juice and Smoothies', 1, 4.6, 25.76737, -80.21388),
    ("Old's Havana", 'Little Havana', 'Cuban', 2, 4.5, 25.76946, -80.22238),
    ("Joe's Stone Crab", 'South Beach', 'Seafood', 4, 4.6, 25.78123, -80.13208),
    ('Prime 112', 'South Beach', 'Steakhouse', 4, 4.5, 25.77687, -80.13456),
    ('Carbone', 'South Beach', 'Italian', 4, 4.5, 25.77862, -80.13869),
    ('Call Me Gaby', 'South Beach', 'Italian', 3, 4.5, 25.77731, -80.13088),
    ('Puerto Sagua', 'South Beach', 'Cuban', 2, 4.5, 25.77815, -80.13713),
    ('La Sandwicherie', 'South Beach', 'Sandwiches', 1, 4.6, 25.78129, -80.12964),
    ('Big Pink', 'South Beach', 'American', 2, 4.4, 25.77757, -80.13471),
    ('Yardbird', 'South Beach', 'Southern', 3, 4.6, 25.78319, -80.1295),
    ('Smith and Wollensky', 'South Beach', 'Steakhouse', 4, 4.4, 25.78643, -80.12973),
    ('Papi Steak', 'South Beach', 'Steakhouse', 4, 4.4, 25.77994, -80.13512),
    ('Caffe Abbracci', 'Coral Gables', 'Italian', 3, 4.6, 25.74761, -80.25889),
    ('Pincho', 'Coral Gables', 'Latin', 1, 4.5, 25.75479, -80.26769),
    ('Bulla Gastrobar', 'Coral Gables', 'Spanish', 3, 4.5, 25.74541, -80.26672),
    ('Threefold Cafe', 'Coral Gables', 'Cafe', 2, 4.6, 25.7461, -80.26368),
    ('GreenStreet Cafe', 'Coconut Grove', 'American', 2, 4.4, 25.72907, -80.24585),
    ('Glass and Vine', 'Coconut Grove', 'American', 3, 4.4, 25.72205, -80.24397),
    ('Ariete', 'Coconut Grove', 'American', 3, 4.6, 25.72643, -80.2422),
    ('Bombay Darbar', 'Coconut Grove', 'Indian', 2, 4.6, 25.73344, -80.24071),
    ('LoKal', 'Coconut Grove', 'Burgers', 2, 4.6, 25.72819, -80.24159),
    ("Monty's Raw Bar", 'Coconut Grove', 'Seafood', 3, 4.3, 25.73011, -80.24835),
    ('Los Felix', 'Coconut Grove', 'Mexican', 3, 4.6, 25.73279, -80.23964),
    ("Shorty's BBQ", 'South Miami', 'BBQ', 2, 4.5, 25.71239, -80.28983),
    ('Whisk Gourmet', 'South Miami', 'Southern', 2, 4.5, 25.70661, -80.29461),
    ('Deli Lane Cafe', 'South Miami', 'Cafe', 2, 4.5, 25.70314, -80.29179),
    ('Sushi Maki', 'South Miami', 'Japanese', 2, 4.3, 25.70265, -80.29859),
]


def load_sample_data():
    """Turn the sample list into the same kind of table a live search makes."""
    rows = []
    for name, neighborhood, cuisine, price, rating, lat, lon in SAMPLE_RESTAURANTS:
        query = urllib.parse.quote(name + " " + neighborhood + " Miami FL")
        rows.append({
            "name": name, "cuisine": cuisine, "address": neighborhood + ", Miami, FL",
            "latitude": lat, "longitude": lon, "rating": rating, "reviews": None,
            "price": price, "open_now": None,
            "maps_url": "https://www.google.com/maps/search/?api=1&query=" + query,
        })
    return pd.DataFrame(rows)
