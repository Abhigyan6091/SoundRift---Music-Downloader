# 🎵 SoundRift

> **Search & Download music from anywhere in the Internet.**

SoundRift is a lightning-fast, premium-designed web application that lets you search for any track, listen to a real-time web audio preview, and download it instantly as a fully-tagged, high-quality MP3 file. 

## ✨ Features

- **🌐 Search the Web:** Type any song, artist, or album, and SoundRift will locate it instantly using the largest audio database on the internet.
- **🔗 Paste Any URL:** Prefer to download directly? Paste a link from over 1,800+ supported sites (Bandcamp, Audiomack, Dailymotion, Vimeo, etc.).
- **🗂️ Massive Playlist Support:** Paste a YouTube playlist URL, and SoundRift will automatically download the whole list, tag them, package them into a `.zip` archive, and send the entire bundle to you instantly.
- **🎧 Real-Time Streaming Previews:** Not sure if it's the right remix? Click *Preview* to stream the audio directly inside the browser using a custom proxy player—before downloading!
- **🖼️ Automatic ID3 Metadata & Album Art:** Every MP3 you download is automatically encoded with the official Thumbnail as the embedded Album Cover, plus the Artist & Title tags, so it looks flawless in your mobile music players.
- **📈 Live Progress UI:** Never wonder if a download is stalled. Track yt-dlp downloads in real-time with a live progress bar powered by Server-Sent Events (SSE).
- **🎨 Premium Dark Aesthetics:** A sleek, glassmorphic UI built in complete vanilla HTML/CSS/JS, featuring a grey-green/emerald glowing theme, live mesh background, equalizer micro-interactions, and floating particles.

## 🚀 How to Run Locally

Follow these steps to get SoundRift running on your own machine.

### 1. Clone the Repository
Open your terminal and clone the project:
```bash
git clone https://github.com/Abhigyan6091/SoundRift.git
cd SoundRift
```

### 2. Install FFmpeg (Required)
SoundRift strictly requires `ffmpeg` to process audio files and embed ID3 metadata (album art, artist, and titles).
- **Windows**: Open PowerShell and run: `winget install ffmpeg` *(Requires restarting terminal afterwards)*
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### 3. Install Python Dependencies
Ensure you have Python 3.9+ installed. Then, install the required packages:
```bash
pip install -r requirements.txt
```
*(This installs `fastapi`, `uvicorn`, `yt-dlp`, `mutagen`, `httpx`, and `python-multipart`)*

### 4. Start the Application
You can now start the FASTAPI server.

**Option A (For Windows Users):**
Inside the project folder, simply double-click the **`start.bat`** file. It will automatically boot the server and open your default web browser!

**Option B (Manual Start):**
Run the following command in your terminal:
```bash
python -m uvicorn main:app --port 8000
```
Then, open your web browser and navigate to **`http://localhost:8000`**.

---

## 💻 Tech Stack
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), Vanilla JavaScript, SSE EventSource.
- **Backend**: Python, [FastAPI](https://fastapi.tiangolo.com/), Uvicorn.
- **Extraction Engine**: [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- **Tagging Engine**: Mutagen + FFmpeg

## ⚖️ Disclaimer
*SoundRift is built purely as an educational programming project showcasing modern Python API integrations, asynchronous programming, Server-Sent Events, and client-side processing. The creators do not condone downloading copyrighted material without explicit permission or licensing from the respective rights holders. Please restrict your use of this tool to legally permissible content (e.g., royalty-free audio, public domain music, or content you own).*
