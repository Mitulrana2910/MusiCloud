import os
import joblib
import requests
from dotenv import load_dotenv
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
from datetime import datetime

# ---------------- Streamlit Config ---------------- #
st.set_page_config(page_title="Musicloud", layout="wide")
st.title("Musicloud")

# ---------------- File URLs ---------------- #
URL_DF = "https://drive.google.com/uc?export=download&id=1CRDB401zws9N7lLycOrXzOSDH7GSuLZS"
URL_SIMILARITY = "https://drive.google.com/uc?export=download&id=1vA4AeZu8eTLc6b1H1aCiOS32WLT4a47A"


# ---------------- Download Files (Only Once) ---------------- #
def download_file(url, path):
    if not os.path.exists(path):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        else:
            st.error(f"Failed to download {path}")
            st.stop()

download_file(URL_DF, "df.pkl")
download_file(URL_SIMILARITY, "similarity.pkl")


# ---------------- Cached Model Loading ---------------- #
@st.cache_resource
def load_models():
    music = joblib.load("df.pkl")
    similarity = joblib.load("similarity.pkl")
    return music, similarity

music, similarity = load_models()
music_list = music['song'].values


# ---------------- Spotify API ---------------- #
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    st.error("⚠ CLIENT_ID or CLIENT_SECRET not found in .env")
    st.stop()

client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# ---------------- Cached Album Cover Fetch ---------------- #
@st.cache_data(show_spinner=False)
def get_song_album_cover_url(song_name, artist_name):
    search_query = f"track:{song_name} artist:{artist_name}"
    results = sp.search(q=search_query, type="track", limit=1)
    if results and results["tracks"]["items"]:
        return results["tracks"]["items"][0]["album"]["images"][0]["url"]
    return "https://i.postimg.cc/0QNxYz4V/social.png"


# ---------------- Recommendation Logic ---------------- #
def recommend(song):
    index = music[music['song'] == song].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    names, posters = [], []
    for i in distances[1:6]:
        artist = music.iloc[i[0]].artist
        posters.append(get_song_album_cover_url(music.iloc[i[0]].song, artist))
        names.append(music.iloc[i[0]].song)

    return names, posters


# ---------------- EVENT MANAGEMENT ---------------- #
EVENT_FILE = "events.json"

@st.cache_data
def load_events():
    try:
        with open(EVENT_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_events(events):
    with open(EVENT_FILE, "w") as f:
        json.dump(events, f, indent=4)
    load_events.clear()  # refresh cache


def add_event(name, time, capacity, charges):
    events = load_events()
    event_id = len(events) + 1
    events.append({
        "event_id": event_id,
        "event_name": name,
        "event_time": time,
        "capacity": capacity,
        "charges": charges,
        "participants": []
    })
    save_events(events)


def participate(event_id, user_name):
    events = load_events()
    for event in events:
        if event["event_id"] == event_id:
            if user_name in event["participants"]:
                return False
            if len(event["participants"]) >= event["capacity"]:
                return False
            event["participants"].append(user_name)
            save_events(events)
            return True
    return False


def delete_event(event_id):
    events = load_events()
    events = [e for e in events if e["event_id"] != event_id]
    for idx, e in enumerate(events):
        e["event_id"] = idx + 1
    save_events(events)


# ---------------- UI ---------------- #
menu = st.sidebar.selectbox(
    "Menu",
    ["Music Recommender", "Playlist (Coming Soon)", "Event Management"]
)

# ------------ MUSIC RECOMMENDER ------------- #
if menu == "Music Recommender":
    selected_song = st.selectbox("Search or type a song", music_list)

    if st.button("Show Recommendation"):
        with st.spinner("Fetching Recommendations..."):
            names, posters = recommend(selected_song)

        cols = st.columns(5)
        for idx, col in enumerate(cols):
            col.text(names[idx])
            col.image(posters[idx])


# ------------ PLAYLIST PLACEHOLDER ------------- #
elif menu == "Playlist (Coming Soon)":
    st.header("🎧 Playlist Feature")
    st.info("🚀 New Playlist feature is coming soon! Stay tuned…")


# ------------ EVENT MANAGEMENT ------------- #
elif menu == "Event Management":
    st.header("Event Management System")
    action = st.radio("Choose Action", ["Add Event", "View Events"])

    # ---------- ADD EVENT ---------- #
    if action == "Add Event":
        with st.form(key="add_event_form"):
            name = st.text_input("Event Name")
            event_date = st.date_input("Select Event Date")
            event_time = st.time_input("Select Event Time")

            capacity = st.number_input("Capacity", min_value=1, step=1)
            charges = st.number_input("Charges", min_value=0, step=1)
            submitted = st.form_submit_button("Add Event")

        if submitted:
            try:
                event_datetime = datetime.combine(event_date, event_time)
                add_event(name, str(event_datetime), capacity, charges)
                st.success("Event added successfully!")
            except Exception as e:
                st.error("⚠ Failed to save event time")
                st.write(e)

    # ---------- VIEW EVENTS ---------- #
    elif action == "View Events":
        events = load_events()

        if not events:
            st.info("No events available.")
        else:
            for event in events:
                st.markdown(f"### {event['event_name']}")
                st.write(f"Time: {event['event_time']}")
                st.write(f"Capacity: {event['capacity']}")
                st.write(f"Participants: {len(event['participants'])}")
                st.write(f"Charges: ${event['charges']}")

                is_full = len(event["participants"]) >= event["capacity"]

                with st.form(key=f"participate_{event['event_id']}"):
                    user_name = st.text_input(
                        "Enter your name",
                        key=f"name_{event['event_id']}"
                    )
                    submitted = st.form_submit_button(
                        "Participate",
                        disabled=is_full
                    )

                    if submitted:
                        if user_name:
                            if participate(event["event_id"], user_name):
                                st.success("You joined the event!")
                            else:
                                st.error("Already joined or event full!")
                        else:
                            st.warning("Enter name first")

                if is_full:
                    st.warning("Event Full!")

                if st.button(f"Delete {event['event_name']}",
                             key=f"delete_{event['event_id']}"):
                    delete_event(event["event_id"])
                    st.success("Event deleted")
