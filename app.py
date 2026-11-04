# app.py
# The Streamlit web app. This file builds the page and connects everyone's code.
# Run it with:  streamlit run app.py

import json

import html

import folium
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from settings import (NEIGHBORHOODS, CUISINES, RATING_CHOICES, SORT_CHOICES,
                      MAX_CALLS_PER_SESSION, SearchError)
from places_api import build_request_body, fetch_places
from sample_data import load_sample_data
from filters import (validate_inputs, parse_min_rating, filter_restaurants, sort_results,
                     pick_random, price_text, rating_text)

st.set_page_config(page_title="Where Should We Eat?", page_icon="🌴", layout="wide")

# Remember things between clicks (Streamlit reruns this file on every click)
if "api_calls" not in st.session_state:
    st.session_state["api_calls"] = 0      # billable Google requests this session
    st.session_state["cache"] = {}         # past searches, so repeats are free
    st.session_state["results"] = None
    st.session_state["center"] = NEIGHBORHOODS["University of Miami"]
    st.session_state["pick"] = None


def get_api_key():
    """Read the key from Streamlit secrets. No key means sample mode."""
    try:
        return st.secrets.get("GOOGLE_PLACES_API_KEY", "").strip()
    except Exception:
        return ""   # no secrets file at all


def run_search(neighborhood, radius, cuisine, prices, rating_choice, open_now, sort_choice):
    """Get results (live or sample), filter them, sort them. Returns (results, center, sample_mode)."""
    validate_inputs(neighborhood, radius, cuisine, prices)
    center = NEIGHBORHOODS[neighborhood]
    min_rating = parse_min_rating(rating_choice)
    api_key = get_api_key()
    sample_mode = api_key == ""

    if sample_mode:
        df = load_sample_data()
    else:
        body = build_request_body(cuisine, center, radius, prices, min_rating, open_now)
        cache_key = json.dumps(body, sort_keys=True)
        if cache_key in st.session_state["cache"]:
            df = st.session_state["cache"][cache_key]
        else:
            if st.session_state["api_calls"] >= MAX_CALLS_PER_SESSION:
                raise SearchError("Safety limit reached for this session. Refresh the page to search more.")
            df, calls = fetch_places(api_key, body)
            st.session_state["api_calls"] += calls
            st.session_state["cache"][cache_key] = df

    results = filter_restaurants(df, center, radius, cuisine, prices, min_rating, open_now, sample_mode)
    return sort_results(results, sort_choice), center, sample_mode


# ===== Sidebar: the search form =====
with st.sidebar:
    st.header("Find a place")
    with st.form("search_form"):
        neighborhood = st.selectbox("Neighborhood", list(NEIGHBORHOODS))
        radius = st.slider("Radius (miles)", 0.25, 5.0, 1.5, 0.25)
        cuisine = st.selectbox("Cuisine", list(CUISINES))
        # A backslash before $ stops Streamlit from treating it as a math symbol
        prices = st.pills("Budget", [1, 2, 3, 4], selection_mode="multi",
                          format_func=lambda level: "\\$" * level)
        rating_choice = st.selectbox("Minimum rating", RATING_CHOICES)
        open_now = st.toggle("Open now")
        sort_choice = st.selectbox("Sort by", SORT_CHOICES)
        submitted = st.form_submit_button("Search", type="primary", width="stretch")

# Search when the button is pressed, or once automatically when the page first loads
if submitted or st.session_state["results"] is None:
    try:
        results, center, _ = run_search(neighborhood, radius, cuisine, prices or [],
                                        rating_choice, open_now, sort_choice)
        st.session_state["results"] = results
        st.session_state["center"] = center
        st.session_state["pick"] = None
        st.session_state["search_label"] = f"{cuisine if cuisine != 'Any' else 'Restaurants'} near {neighborhood}"
    except SearchError as error:
        st.session_state["results"] = pd.DataFrame()
        st.error(str(error))
    except Exception as error:   # anything unexpected still gets a message
        st.session_state["results"] = pd.DataFrame()
        st.error(f"Something went wrong: {error}")

results = st.session_state["results"]
center = st.session_state["center"]

# Show which mode we're in (placed after the search so the request count is current)
sample_mode = get_api_key() == ""
if sample_mode:
    st.sidebar.caption("Sample mode: no API key set. Ratings and prices are approximate.")
else:
    st.sidebar.caption(f"Live Google data. {st.session_state['api_calls']} requests used this session.")

# ===== Header =====
st.title("🌴 Where Should We Eat?")
st.caption("Miami restaurant finder with real ratings and prices from Google. BTE 320, Fall 2026.")

if results is None or len(results) == 0:
    st.info("No restaurants match. Try a bigger radius, a lower minimum rating, or more price levels.")
    if sample_mode and open_now:
        st.caption("Note: Open now only works with live Google data.")
    st.stop()

st.subheader(st.session_state.get("search_label", "Results"))

# ===== Summary numbers =====
col1, col2, col3, col4 = st.columns(4)
col1.metric("Restaurants found", len(results))
col2.metric("Average rating", f"{results['rating'].mean():.2f} ★" if results["rating"].notna().any() else "N/A")
col3.metric("Closest", f"{results['distance'].min():.2f} mi")
top = results.sort_values("rating", ascending=False).iloc[0]
col4.metric("Top rated", top["name"])

# ===== Pick for Me =====
if st.button("🎲 Pick for Me", type="primary"):
    st.session_state["pick"] = pick_random(results)["name"]

if st.session_state["pick"] is not None:
    choice = results[results["name"] == st.session_state["pick"]].iloc[0]
    st.success(f"**Let's eat at {choice['name']}!**  "
               f"{rating_text(choice['rating'], choice['reviews'])} · "
               f"{price_text(choice['price']).replace('$', '\\$')} · "   # \\$ shows a plain dollar sign
               f"{choice['distance']:.2f} mi away · [Open in Google Maps]({choice['maps_url']})")

# ===== Results: list and map =====
tab_list, tab_map = st.tabs(["📋 List", "🗺️ Map"])

with tab_list:
    table = pd.DataFrame({
        "Restaurant": results["name"],
        "Rating": results["rating"],
        "Reviews": results["reviews"],
        "Price": results["price"].apply(price_text),
        "Type": results["cuisine"],
        "Distance": results["distance"],
        "Open now": results["open_now"].map({True: "Open", False: "Closed"}).fillna(""),
        "Google Maps": results["maps_url"],
    })
    st.dataframe(
        table, hide_index=True, width="stretch",
        column_config={
            "Rating": st.column_config.NumberColumn(format="%.1f ★"),
            "Reviews": st.column_config.NumberColumn(format="%d"),
            "Distance": st.column_config.NumberColumn(format="%.2f mi"),
            "Google Maps": st.column_config.LinkColumn(display_text="Open map"),
        },
    )

with tab_map:
    # Interactive map made with folium, using Esri's free street map (no key needed)
    m = folium.Map(location=center, zoom_start=14, tiles="Esri.WorldStreetMap")
    folium.Marker(center, tooltip="Search center",
                  icon=folium.Icon(color="gray", icon="home")).add_to(m)
    for _, r in results.iterrows():
        is_pick = r["name"] == st.session_state["pick"]
        popup = (f"<b>{html.escape(r['name'])}</b><br>{rating_text(r['rating'], r['reviews'])}"
                 f"<br>{price_text(r['price'])}")
        folium.Marker([r["latitude"], r["longitude"]], tooltip=r["name"],
                      popup=folium.Popup(popup, max_width=250),
                      icon=folium.Icon(color="red" if is_pick else "blue")).add_to(m)
    components.html(m.get_root().render(), height=520)
    st.caption("Click a pin to see its name, rating, and price. The red pin is your Pick for Me.")
