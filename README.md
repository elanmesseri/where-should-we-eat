# Where Should We Eat?

A Miami restaurant finder web app with real ratings, review counts, and price levels from the Google Places API. Built with Streamlit for BTE 320, Fall 2026.

## Run it on your own computer

1. Install Python 3.9 or newer.
2. Open a terminal in this folder and install the libraries:

       pip install -r requirements.txt

3. (Optional, for live Google data) Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste your API key into it. Without a key, the app runs in sample mode with approximate data.
4. Start the app:

       streamlit run app.py

5. It opens in your browser at http://localhost:8501.

## Put it online with a real link (free)

1. Upload this folder to a GitHub repository. Do NOT upload `secrets.toml` (the `.gitignore` file already blocks it).
2. Go to share.streamlit.io and sign in with GitHub.
3. Create a new app, choose your repository, and set the main file to `app.py`.
4. Before deploying, open the advanced settings and paste this into Secrets:

       GOOGLE_PLACES_API_KEY = "your-key-here"

5. Deploy. You get a link ending in `.streamlit.app` that works on any laptop or phone.

## Run the tests

    python test_app.py

The tests use fake Google responses, so they never use real API requests.

## Files

| File | What it does |
|---|---|
| app.py | The Streamlit web page: search form, results, Pick for Me, map |
| places_api.py | Sends searches to the Google Places API and reads the replies |
| filters.py | Distance, filtering, sorting, and random picking |
| settings.py | Neighborhoods, cuisines, price levels, and safety limits |
| sample_data.py | Backup list of 63 Miami restaurants for sample mode |
| test_app.py | Automated tests |

## Libraries used

* **Streamlit** builds the web interface: the search form, buttons, summary numbers, table, and tabs.
* **requests** sends search requests to the Google Places API.
* **pandas** stores results as a table for filtering, sorting, and averages.
* **folium** draws the interactive map with clickable pins.

## Notes

Sample mode ratings, prices, and map locations are approximate and were entered by the team.
Each live search uses at most 2 Google requests, repeat searches are free, and each session is capped at 60 requests.
