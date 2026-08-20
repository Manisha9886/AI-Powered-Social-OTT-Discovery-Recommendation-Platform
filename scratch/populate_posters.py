import os
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

LOOKUP_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "movie_lookup.json")
if not os.path.exists(LOOKUP_PATH):
    LOOKUP_PATH = os.path.join(os.getcwd(), "data", "processed", "movie_lookup.json")

print(f"Loading {LOOKUP_PATH}...")
with open(LOOKUP_PATH, 'r', encoding='utf-8') as f:
    movie_lookup = json.load(f)

print(f"Loaded {len(movie_lookup)} movies.")

def fetch_poster_for_movie(movie):
    title = movie.get("title")
    year = movie.get("release_year")
    if not title:
        return None
        
    try:
        query_url = f"http://www.omdbapi.com/?t={urllib.parse.quote(title)}&y={year}&apikey=trilogy"
        req = urllib.request.Request(query_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            poster = data.get("Poster")
            if poster and poster.startswith("http") and "N/A" not in poster:
                return (str(movie.get("movie_id")), poster)
    except Exception:
        pass
        
    try:
        query_url = f"http://www.omdbapi.com/?t={urllib.parse.quote(title)}&apikey=trilogy"
        req = urllib.request.Request(query_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            poster = data.get("Poster")
            if poster and poster.startswith("http") and "N/A" not in poster:
                return (str(movie.get("movie_id")), poster)
    except Exception:
        pass
        
    return None

movies_list = list(movie_lookup.values())
# Process top 300 movies in parallel for speed
movies_to_process = movies_list[:300]
print(f"Fetching official HD posters for top {len(movies_to_process)} movies...")

updated_count = 0
with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(fetch_poster_for_movie, m) for m in movies_to_process]
    for future in as_completed(futures):
        res = future.result()
        if res:
            m_id, poster_url = res
            if m_id in movie_lookup:
                movie_lookup[m_id]["poster_path"] = poster_url
                updated_count += 1

print(f"Successfully updated {updated_count} official movie posters!")

with open(LOOKUP_PATH, 'w', encoding='utf-8') as f:
    json.dump(movie_lookup, f, indent=2, ensure_ascii=False)

print("Saved updated movie_lookup.json!")
