import os
import json
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
LOOKUP_PATH = os.path.join(PROCESSED_DIR, 'movie_lookup.json')

OMDB_KEYS = ["trilogy", "7272990a", "b58832a8", "852467d5"]

def fetch_poster_multi_strategy(movie_id, title, release_year):
    strategies = [
        # Strategy 1: Full Title
        title,
        # Strategy 2: Title before colon
        title.split(":")[0] if ":" in title else title,
        # Strategy 3: Title before dash
        title.split("-")[0] if "-" in title else title,
        # Strategy 4: Clean title (alphanumeric only)
        re.sub(r'[^a-zA-Z0-9 ]', '', title)
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    clean_strategies = []
    for s in strategies:
        s_clean = s.strip()
        if s_clean and s_clean not in seen:
            seen.add(s_clean)
            clean_strategies.append(s_clean)

    for query_title in clean_strategies:
        encoded_title = requests.utils.quote(query_title)
        for k in OMDB_KEYS:
            try:
                # Try with release year first
                url = f"http://www.omdbapi.com/?apikey={k}&t={encoded_title}&y={release_year}"
                resp = requests.get(url, timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    poster = data.get("Poster")
                    if poster and poster != "N/A" and poster.startswith("http"):
                        return movie_id, poster

                # Try without year
                url_no_year = f"http://www.omdbapi.com/?apikey={k}&t={encoded_title}"
                resp2 = requests.get(url_no_year, timeout=3)
                if resp2.status_code == 200:
                    data2 = resp2.json()
                    poster2 = data2.get("Poster")
                    if poster2 and poster2 != "N/A" and poster2.startswith("http"):
                        return movie_id, poster2
            except Exception:
                pass

    return movie_id, None

def populate_posters():
    if not os.path.exists(LOOKUP_PATH):
        print(f"Error: {LOOKUP_PATH} not found.")
        return

    print("Loading movie_lookup.json...")
    with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
        movies = json.load(f)

    to_update = []
    for mid, mdata in movies.items():
        poster = mdata.get("poster_path")
        if not poster or not poster.startswith("http"):
            to_update.append((mid, mdata.get("title", ""), mdata.get("release_year", "")))

    print(f"Found {len(to_update)} movies needing HD poster updates out of {len(movies)} total movies.")

    if not to_update:
        print("All movies already have valid poster paths!")
        return

    print("Fetching HD posters with multi-strategy title cleaning in parallel...")
    updated_count = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(fetch_poster_multi_strategy, mid, title, year): mid for mid, title, year in to_update}
        for future in as_completed(futures):
            mid, new_poster = future.result()
            if new_poster:
                movies[mid]["poster_path"] = new_poster
                updated_count += 1
                if updated_count % 100 == 0 or updated_count == len(to_update):
                    print(f"Successfully populated {updated_count}/{len(to_update)} movie posters...")

    elapsed = round(time.time() - start_time, 2)
    print(f"\nFinished populating {updated_count} additional HD movie poster URLs in {elapsed}s!")

    with open(LOOKUP_PATH, 'w', encoding='utf-8') as f:
        json.dump(movies, f, indent=2)

    print("Saved updated movie_lookup.json!")

if __name__ == "__main__":
    populate_posters()
