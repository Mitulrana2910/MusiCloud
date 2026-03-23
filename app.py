import os
import joblib
import requests
import json
import pandas as pd
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# ---------------- Load Configurations ---------------- #
load_dotenv()
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
EVENT_FILE = "events.json"
PLAYLIST_FILE = "playlists.json"  # New file for likes
DF_PATH = "df.pkl"
SIMILARITY_PATH = "similarity.pkl"

# ---------------- Load Models ---------------- #
try:
    music = joblib.load(DF_PATH)
    similarity = joblib.load(SIMILARITY_PATH)
except:
    music = pd.DataFrame(columns=['song', 'artist'])
    similarity = []

headers = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": RAPIDAPI_HOST
}


# ---------------- Helper: Spotify Data ---------------- #
def get_spotify_data(song_name, artist_name):
    """Fetches both cover art and 30-second preview URL."""
    if not RAPIDAPI_KEY:
        return {"poster": "https://i.postimg.cc/0QNxYz4V/social.png", "preview": None}

    url = f"https://{RAPIDAPI_HOST}/search/"
    querystring = {"q": f"{song_name} {artist_name}", "type": "tracks", "offset": "0", "limit": "1"}

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=5)
        if response.status_code == 200:
            data = response.json()
            tracks = data.get("tracks", {}).get("items", [])
            if tracks:
                track_data = tracks[0]["data"]
                return {
                    "poster": track_data["albumOfTrack"]["coverArt"]["sources"][0]["url"],
                    "preview": track_data.get("preview_url")  # RapidAPI Spotify preview link
                }
    except Exception as e:
        print(f"RapidAPI Error: {e}")

    return {"poster": "https://i.postimg.cc/0QNxYz4V/social.png", "preview": None}


# ==================== Flask Routes ==================== #

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/songs')
def get_songs():
    return jsonify(music['song'].tolist())


@app.route('/api/recommend')
def api_recommend():
    song_title = request.args.get('song')
    if not song_title or song_title not in music['song'].values:
        return jsonify({"error": "Song not found"}), 404

    idx = music[music['song'] == song_title].index[0]
    distances = sorted(list(enumerate(similarity[idx])), reverse=True, key=lambda x: x[1])

    recommended_songs = []
    for i in distances[1:6]:
        row = music.iloc[i[0]]
        spotify_info = get_spotify_data(row.song, row.artist)
        recommended_songs.append({
            "title": row.song,
            "artist": row.artist,
            "poster": spotify_info["poster"],
            "preview": spotify_info["preview"]
        })
    return jsonify(recommended_songs)


# --- New: Playlist/Like Logic ---
@app.route('/api/like', methods=['POST'])
def api_like():
    song_data = request.json
    try:
        if os.path.exists(PLAYLIST_FILE):
            with open(PLAYLIST_FILE, "r") as f:
                playlist = json.load(f)
        else:
            playlist = []

        # Check for duplicates
        if not any(s['title'] == song_data['title'] for s in playlist):
            playlist.append(song_data)
            with open(PLAYLIST_FILE, "w") as f:
                json.dump(playlist, f, indent=4)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/playlist')
def get_playlist():
    if os.path.exists(PLAYLIST_FILE):
        with open(PLAYLIST_FILE, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])


# (Keeping your existing Event Routes below...)
@app.route('/api/events', methods=['GET', 'POST', 'DELETE'])
def api_events():
    # ... (Keep your existing events code here as provided in your original app.py)
    pass


if __name__ == '__main__':
    app.run(debug=True, port=5000)