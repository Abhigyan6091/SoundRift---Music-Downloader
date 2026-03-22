import asyncio
import os
import shutil
import tempfile
import re
import json
from pathlib import Path
from typing import Optional
from urllib.parse import quote

import httpx
import yt_dlp
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Soundrift API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Models ──────────────────────────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str
    source: str = "youtube"

class DownloadRequest(BaseModel):
    url: str
    title: str = "track"
    client_id: str = "default"

# ── Global Progress State ───────────────────────────────────────────────────

# format: { "client_id": {"percent": 0.0, "status": "downloading"} }
download_progress = {}

# ── Helpers ─────────────────────────────────────────────────────────────────

SOURCE_PREFIXES = {
    "youtube": "ytsearch10:",
}


def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "", name).strip()[:80]


def validate_url(url: str) -> None:
    if not url.startswith(("http://", "https://")):
        raise HTTPException(400, "Invalid URL — must start with http:// or https://")


def _fmt_duration(seconds) -> str:
    if not seconds:
        return ""
    seconds = int(seconds)
    if seconds >= 3600:
        return f"{seconds // 3600}:{(seconds % 3600) // 60:02d}:{seconds % 60:02d}"
    return f"{seconds // 60}:{seconds % 60:02d}"


async def search_music_source(query: str, source: str = "youtube") -> list[dict]:
    prefix = SOURCE_PREFIXES.get(source, "ytsearch10:")

    def _search():
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{prefix}{query}", download=False)
            entries = info.get("entries", [])
            results = []
            for e in entries:
                if not e:
                    continue
                vid_url = e.get("url") or e.get("webpage_url", "")
                if source == "youtube" and e.get("id") and not vid_url.startswith("http"):
                    vid_url = f"https://www.youtube.com/watch?v={e['id']}"

                results.append({
                    "title": e.get("title", "Unknown"),
                    "url": vid_url,
                    "duration": e.get("duration_string") or _fmt_duration(e.get("duration")),
                    "uploader": e.get("uploader") or e.get("channel", ""),
                    "thumbnail": e.get("thumbnail") or e.get("thumbnails", [{}])[-1].get("url", ""),
                    "view_count": e.get("view_count", 0),
                    "source": source,
                })
            return results

    return await asyncio.to_thread(_search)


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = Path(__file__).parent / "index.html"
    if html_path.exists():
        return HTMLResponse(content=html_path.read_text(encoding="utf-8"), media_type="text/html")
    return HTMLResponse("<h1>Soundrift API — open /docs</h1>")


@app.post("/search")
async def search_music(req: SearchRequest):
    if not req.query.strip():
        raise HTTPException(400, "Query cannot be empty")
    source = "youtube"
    try:
        results = await search_music_source(req.query, source)
        return {"results": results, "source": source}
    except Exception as e:
        raise HTTPException(500, f"Search failed: {str(e)}")


@app.get("/progress/{client_id}")
async def get_progress(client_id: str, request: Request):
    """Server-Sent Events endpoint to stream yt-dlp download progress."""
    async def event_generator():
        # Wait until progress dict is populated for this client
        while client_id not in download_progress:
            if await request.is_disconnected():
                return
            await asyncio.sleep(0.5)

        last_percent = -1
        while True:
            if await request.is_disconnected():
                break
                
            current = download_progress.get(client_id, {})
            percent = current.get("percent", 0.0)
            status = current.get("status", "pending")
            
            if percent != last_percent or status != current.get("last_status"):
                current["last_status"] = status
                last_percent = percent
                data = json.dumps({"percent": round(percent, 1), "status": status})
                yield f"data: {data}\n\n"
            
            if status == "done":
                break
                
            await asyncio.sleep(0.5)
            
        # Clean up
        if client_id in download_progress:
            del download_progress[client_id]

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/download")
async def download_music(req: DownloadRequest):
    """Download single tracks or playlists, apply ID3 tags, and return MP3 or ZIP."""
    validate_url(req.url)

    tmp_dir = tempfile.mkdtemp()
    out_template = os.path.join(tmp_dir, "%(title)s.%(ext)s")

    def progress_hook(d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total:
                percent = (d.get('downloaded_bytes', 0) / total) * 100
                download_progress[req.client_id] = {"percent": percent, "status": "downloading"}
        elif d['status'] == 'finished':
            download_progress[req.client_id] = {"percent": 100.0, "status": "processing (ffmpeg)"}

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": out_template,
        "quiet": True,
        "no_warnings": True,
        # Playlist settings: extract all
        "extract_flat": False,
        # progress callback
        "progress_hooks": [progress_hook],
        # Required to embed thumbnail
        "writethumbnail": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            {
                # Embed the thumbnail as album art
                "key": "EmbedThumbnail",
            },
            {
                # Embed title, artist, etc into ID3 tags
                "key": "FFmpegMetadata",
                "add_metadata": True,
            }
        ],
    }

    # Initialize progress
    download_progress[req.client_id] = {"percent": 0.0, "status": "starting"}

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([req.url])

    try:
        await asyncio.to_thread(_download)
        download_progress[req.client_id] = {"percent": 100.0, "status": "done"}
    except Exception as e:
        download_progress[req.client_id] = {"percent": 0.0, "status": "error"}
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(500, f"Download failed: {str(e)}")

    # Check contents of the temp dir
    mp3_files = list(Path(tmp_dir).glob("*.mp3"))
    if not mp3_files:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise HTTPException(500, "Conversion to MP3 failed — is ffmpeg and mutagen installed?")

    # 1. PLAYLIST DOWNLOAD (ZIP)
    if len(mp3_files) > 1:
        safe_title = sanitize_filename(req.title) or "playlist"
        zip_path = os.path.join(tempfile.gettempdir(), f"{safe_title}.zip")
        
        def _zip():
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', tmp_dir)
            
        await asyncio.to_thread(_zip)
        
        def iterzip():
            with open(zip_path, "rb") as f:
                yield from f
            os.remove(zip_path)
            shutil.rmtree(tmp_dir, ignore_errors=True)
            
        encoded_filename = quote(f"{safe_title}.zip")
        return StreamingResponse(
            iterzip(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"},
        )

    # 2. SINGLE TRACK DOWNLOAD (MP3)
    mp3_path = mp3_files[0]
    safe_title = sanitize_filename(req.title) or "track"

    def iterfile():
        with open(mp3_path, "rb") as f:
            yield from f
        shutil.rmtree(tmp_dir, ignore_errors=True)

    filename = f"{safe_title}.mp3"
    encoded_filename = quote(filename)
    return StreamingResponse(
        iterfile(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": f"attachment; filename*=utf-8''{encoded_filename}"},
    )


@app.get("/stream")
async def stream_audio(url: str):
    """Proxy the raw audio stream from YouTube directly to the browser for instant preview."""
    validate_url(url)

    def _get_url():
        ydl_opts = {
            "quiet": True, 
            "no_warnings": True, 
            "format": "bestaudio/best"
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # We must set download=False; this fetches the streaming URL
            info = ydl.extract_info(url, download=False)
            return info.get("url")

    try:
        stream_url = await asyncio.to_thread(_get_url)
        if not stream_url:
            raise ValueError("No stream URL extracted.")
    except Exception as e:
        raise HTTPException(500, f"Could not extract stream: {str(e)}")

    client = httpx.AsyncClient()
    
    async def proxy_stream():
        try:
            # Setting follow_redirects=True is crucial for some yt URLs
            async with client.stream("GET", stream_url, follow_redirects=True) as response:
                if response.status_code != 200:
                    yield b""
                    return
                async for chunk in response.aiter_bytes():
                    yield chunk
        finally:
            await client.aclose()

    return StreamingResponse(proxy_stream(), media_type="audio/mpeg")


@app.get("/preview")
async def preview_info(url: str):
    """Return metadata for a single URL."""
    validate_url(url)

    def _info():
        ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)

    try:
        info = await asyncio.to_thread(_info)
        return {
            "title": info.get("title"),
            "uploader": info.get("uploader"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration_string") or _fmt_duration(info.get("duration")),
        }
    except Exception as e:
        raise HTTPException(500, str(e))
