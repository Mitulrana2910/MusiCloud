# 🎵 Musicloud AI

A modern, high-performance music recommendation engine featuring a **Glassmorphism UI**, real-time **Spotify Previews**, and an **AI-driven** recommendation system using TF-IDF and Cosine Similarity.

## ✨ New Features

- **💎 Glassmorphism UI**: A stunning, frosted-glass interface built with Tailwind CSS.
- **🎧 Real-time Previews**: Listen to 30-second Spotify track previews directly in the browser.
- **❤️ Liked Collection**: Save your favorite recommendations to a persistent "Liked Collection" (Playlist).
- **🤖 AI Recommendations**: Content-based filtering analyzing song metadata to find your perfect vibe.
- **📅 Event Management**: Full-stack system to create music events, manage capacity, and register participants.

## 📁 Project Structure

```
├── app.py                 # Flask Backend (API & Routes)
├── data_cleaning.py       # ML Pipeline (TF-IDF & Similarity Generation)
├── templates/
│   └── index.html         # Frontend (Tailwind CSS & Vanilla JS)
├── static/
│   ├── favicon.ico        # App Icon
│   └── music_icon.svg     # Custom Branding SVG
├── df.pkl                 # Processed Dataframe
├── similarity.pkl         # Cosine Similarity Matrix
├── playlists.json         # Storage for Liked Songs
├── events.json            # Storage for Event Data
└── .env                   # RapidAPI Credentials
```

## 🚀 Installation & Setup

### 1. Clone & Navigate
```bash
git clone <your-repo-url>
cd musicloud
```

### 2. Install Dependencies
```bash
pip install flask pandas scikit-learn joblib nltk python-dotenv requests
```

### 3. API Configuration
Create a `.env` file in the root directory and add your **RapidAPI (Spotify23)** credentials:
```env
RAPIDAPI_KEY=your_key_here
RAPIDAPI_HOST=rapid_api_link
```

### 4. Initialize the AI Model
If you haven't generated the similarity matrices yet, run:
```bash
python data_cleaning.py
```

### 5. Launch the App
```bash
python app.py
```


## 🎯 How It Works

### Music Discovery
1. **Search**: Start typing a song name. The AI provides real-time autocomplete suggestions.
2. **Recommend**: Click "Show Recommendation" to trigger the Cosine Similarity engine.
3. **Preview**: Click the play button on any card to hear the track via the Spotify API.
4. **Like**: Click the ❤️ icon to save a song to your "Liked Collection" tab.

### Event Management
- Create events with specific dates, pricing, and capacity.
- The system automatically handles "Full" status once capacity is reached.
- All data persists in `events.json`.

## 🔧 Tech Stack

- **Backend**: Python / Flask
- **Frontend**: HTML5 / Tailwind CSS / Google Material Symbols
- **Machine Learning**: Scikit-learn (TF-IDF Vectorizer), Cosine Similarity
- **Data Handling**: Pandas, JSON, Joblib
- **APIs**: Spotify (via RapidAPI)

## 🤝 Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🎉 Acknowledgments

- Spotify Million Song Dataset for the core data.
- The Glassmorphism design movement for UI inspiration.
```

### Key Changes Made to your README:
1.  **Framework Update**: Changed references from **Streamlit** to **Flask**.
2.  **UI Description**: Added **Glassmorphism** and **Tailwind CSS** to the tech stack.
3.  **Feature Updates**: Added the **Like (Heart) Button** and **Quick Spotify Preview** features.
4.  **API Update**: Reflected the use of **RapidAPI** instead of the standard Spotipy library.
5.  **Installation**: Updated the run command to `python app.py` and included the template folder structure.
