# 🎵 Soundrift — Music Downloader

A FastAPI app that searches **YouTube, SoundCloud, and 1800+ sites** for music and lets users download tracks as MP3.

---

## Features

- 🔍 **Multi-source search** — YouTube & SoundCloud
- 🔗 **Paste any URL** — download from 1800+ supported sites (Bandcamp, Dailymotion, Vimeo, etc.)
- 🎨 **Premium dark UI** — animated gradients, glassmorphism, floating particles
- ⚡ **Streaming downloads** — no files stored on disk permanently

---

## Requirements

- Python 3.10+
- **ffmpeg** must be installed on your system

### Install ffmpeg

**Ubuntu / Debian**
```bash
sudo apt install ffmpeg
```

**macOS**
```bash
brew install ffmpeg
```

**Windows**
Download from https://ffmpeg.org/download.html and add to PATH.

---

## Setup & Run

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn main:app --reload --port 8000
```

Then open your browser at: **http://localhost:8000**

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Serves the web UI |
| `POST` | `/search` | Search YouTube/SoundCloud → returns list of tracks |
| `POST` | `/download` | Download from any supported URL, convert to MP3, stream back |
| `GET` | `/preview?url=...` | Fetch metadata for a single track |

### Example: Search YouTube
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Daft Punk Get Lucky", "source": "youtube"}'
```

### Example: Search SoundCloud
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "lo-fi chill beats", "source": "soundcloud"}'
```

### Example: Download
```bash
curl -X POST http://localhost:8000/download \
  -H "Content-Type: application/json" \
  -d '{"url": "https://soundcloud.com/artist/track", "title": "My Track"}' \
  --output "My Track.mp3"
```

---

## Project Structure

```
SoundRift/
├── main.py           ← FastAPI backend (multi-source)
├── index.html        ← Premium dark UI
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Notes

- Downloads are streamed directly — no files are stored on disk permanently.
- Audio quality: 192 kbps MP3 (via ffmpeg post-processing).
- Accepts URLs from any site supported by yt-dlp (1800+).
- For personal / educational use only. Respect copyright laws in your country.

---

## Disclaimer

This tool is provided for **personal and educational use only**. Downloading copyrighted content without permission may violate the terms of service of the source platform and the copyright laws in your jurisdiction. The authors are not responsible for any misuse.
