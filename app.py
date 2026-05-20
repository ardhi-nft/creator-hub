#!/usr/bin/env python3
"""Creator Hub — Simple content creator toolkit"""

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
import os
import time
import uuid
import httpx
import subprocess
import re
import pysrt
from datetime import datetime

app = FastAPI(title="Creator Hub")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "creator.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
AI_API = "http://127.0.0.1:20128/v1"
AI_KEY = os.environ.get("AI_API_KEY", "")

# Mount static
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            content TEXT,
            platform TEXT,
            style TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS thumbnails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            prompt TEXT,
            filepath TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            platform TEXT,
            content TEXT,
            media_path TEXT,
            scheduled_at TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS captions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            platform TEXT,
            hashtags TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)
    conn.close()

init_db()

async def ai_chat(system_prompt: str, user_prompt: str, model: str = "anthropic/claude-sonnet-4"):
    """Call AI via 9Router"""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{AI_API}/chat/completions",
            headers={"Authorization": f"Bearer {AI_KEY}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "max_tokens": 2000
            }
        )
        data = resp.json()
        return data["choices"][0]["message"]["content"]

# ============ PAGES ============

@app.get("/", response_class=HTMLResponse)
async def index():
    with open(os.path.join(BASE_DIR, "templates", "index.html")) as f:
        return f.read()

# ============ SCRIPT GENERATOR ============

@app.post("/api/script/generate")
async def generate_script(request: Request):
    body = await request.json()
    topic = body.get("topic", "")
    platform = body.get("platform", "youtube")  # youtube, tiktok, instagram, twitter
    style = body.get("style", "informative")  # informative, entertaining, educational, storytelling
    duration = body.get("duration", "60")  # seconds
    
    system = f"""Kamu adalah scriptwriter profesional untuk konten {platform}. 
Buat script yang engaging, hook kuat di awal, dan CTA di akhir.
Format output:
- HOOK (3 detik pertama)
- BODY (isi utama)
- CTA (call to action)
Durasi target: {duration} detik. Style: {style}.
Tulis dalam Bahasa Indonesia kecuali diminta lain."""

    content = await ai_chat(system, f"Buatkan script tentang: {topic}")
    
    conn = get_db()
    conn.execute("INSERT INTO scripts (title, content, platform, style) VALUES (?,?,?,?)",
                 (topic, content, platform, style))
    conn.commit()
    conn.close()
    
    return {"status": "ok", "script": content}

# ============ CAPTION & HASHTAG ============

@app.post("/api/caption/generate")
async def generate_caption(request: Request):
    body = await request.json()
    topic = body.get("topic", "")
    platform = body.get("platform", "instagram")
    tone = body.get("tone", "casual")  # casual, professional, funny, inspirational
    
    system = f"""Kamu adalah social media expert. Buat caption {platform} yang viral.
Include:
- Caption utama (engaging, sesuai tone: {tone})
- 5-10 hashtag relevan
- Emoji yang pas
Format: caption dulu, lalu hashtags di baris terpisah."""

    content = await ai_chat(system, f"Buat caption untuk: {topic}")
    
    conn = get_db()
    conn.execute("INSERT INTO captions (content, platform, hashtags) VALUES (?,?,?)",
                 (content, platform, ""))
    conn.commit()
    conn.close()
    
    return {"status": "ok", "caption": content}

# ============ HOOK IDEAS ============

@app.post("/api/hooks/generate")
async def generate_hooks(request: Request):
    body = await request.json()
    topic = body.get("topic", "")
    count = body.get("count", 5)
    
    system = """Kamu adalah viral content strategist. Buat hook/opening lines yang bikin orang stop scrolling.
Setiap hook harus:
- Maksimal 1-2 kalimat
- Trigger curiosity atau emotion
- Cocok untuk short-form video (Reels/TikTok/Shorts)
Format: numbered list."""

    content = await ai_chat(system, f"Buat {count} hook ideas untuk topik: {topic}")
    
    return {"status": "ok", "hooks": content}

# ============ THUMBNAIL IDEAS ============

@app.post("/api/thumbnail/ideas")
async def thumbnail_ideas(request: Request):
    body = await request.json()
    topic = body.get("topic", "")
    
    system = """Kamu adalah thumbnail designer expert untuk YouTube.
Buat 3 konsep thumbnail yang CTR tinggi. Untuk setiap konsep, jelaskan:
- Visual utama (apa yang ada di gambar)
- Text overlay (maksimal 3-4 kata, bold)
- Color scheme
- Emotion/expression kalau ada orang
Format yang jelas dan actionable."""

    content = await ai_chat(system, f"Buat konsep thumbnail untuk video: {topic}")
    
    return {"status": "ok", "ideas": content}

# ============ CONTENT CALENDAR ============

@app.post("/api/schedule/create")
async def create_schedule(request: Request):
    body = await request.json()
    title = body.get("title", "")
    platform = body.get("platform", "")
    content = body.get("content", "")
    scheduled_at = body.get("scheduled_at", "")
    
    conn = get_db()
    conn.execute("INSERT INTO schedules (title, platform, content, scheduled_at) VALUES (?,?,?,?)",
                 (title, platform, content, scheduled_at))
    conn.commit()
    conn.close()
    
    return {"status": "ok", "message": "Scheduled"}

@app.get("/api/schedule/list")
async def list_schedules():
    conn = get_db()
    rows = conn.execute("SELECT * FROM schedules ORDER BY scheduled_at ASC").fetchall()
    conn.close()
    return {"status": "ok", "schedules": [dict(r) for r in rows]}

@app.delete("/api/schedule/{id}")
async def delete_schedule(id: int):
    conn = get_db()
    conn.execute("DELETE FROM schedules WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return {"status": "ok"}

# ============ CONTENT IDEAS ============

@app.post("/api/ideas/generate")
async def generate_ideas(request: Request):
    body = await request.json()
    niche = body.get("niche", "")
    platform = body.get("platform", "youtube")
    count = body.get("count", 10)
    
    system = f"""Kamu adalah content strategist untuk {platform}.
Buat {count} ide konten yang trending dan punya potensi viral.
Untuk setiap ide:
- Judul/topic
- Kenapa ini bisa viral (1 kalimat)
- Difficulty (Easy/Medium/Hard)
Format: numbered list yang rapi."""

    content = await ai_chat(system, f"Buat ide konten untuk niche: {niche}")
    
    return {"status": "ok", "ideas": content}

# ============ SEO TITLE & DESCRIPTION ============

@app.post("/api/seo/generate")
async def generate_seo(request: Request):
    body = await request.json()
    topic = body.get("topic", "")
    platform = body.get("platform", "youtube")
    
    system = f"""Kamu adalah SEO expert untuk {platform}. Buat:
1. 3 variasi judul (SEO-optimized, clickable, under 60 chars)
2. Deskripsi (SEO-friendly, 150-200 kata, include keywords natural)
3. Tags/keywords (10-15 relevant tags)
Format yang jelas dengan section headers."""

    content = await ai_chat(system, f"Buat SEO content untuk: {topic}")
    
    return {"status": "ok", "seo": content}

# ============ HISTORY ============

@app.get("/api/history/scripts")
async def history_scripts():
    conn = get_db()
    rows = conn.execute("SELECT * FROM scripts ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return {"status": "ok", "scripts": [dict(r) for r in rows]}

@app.get("/api/history/captions")
async def history_captions():
    conn = get_db()
    rows = conn.execute("SELECT * FROM captions ORDER BY created_at DESC LIMIT 50").fetchall()
    conn.close()
    return {"status": "ok", "captions": [dict(r) for r in rows]}

# ============ AUTO-CLIP ============

ENGAGEMENT_KEYWORDS = [
    # Questions / curiosity
    "kenapa", "gimana", "bagaimana", "apa", "siapa", "kapan", "dimana",
    "why", "how", "what", "who", "when", "where",
    # Emotional triggers
    "gila", "wow", "anjir", "asli", "serius", "beneran", "ternyata",
    "rahasia", "secret", "shocking", "insane", "crazy", "amazing",
    # CTA / engagement
    "subscribe", "like", "comment", "share", "follow",
    # Conflict / tension
    "tapi", "masalahnya", "problem", "but", "however", "actually",
    "salah", "wrong", "mistake", "jangan", "never", "stop",
    # Value signals
    "tips", "trick", "hack", "cara", "tutorial", "gratis", "free",
    "pertama", "first", "penting", "important", "wajib", "must"
]

def analyze_srt_engagement(srt_path: str):
    """Analyze SRT file and score each segment by engagement potential"""
    subs = pysrt.open(srt_path)
    
    # Score each subtitle line
    scored_segments = []
    for sub in subs:
        text = sub.text.lower().replace('\n', ' ')
        score = 0
        
        # Keyword scoring
        for kw in ENGAGEMENT_KEYWORDS:
            if kw in text:
                score += 2
        
        # Question marks = curiosity
        score += text.count('?') * 3
        
        # Exclamation = emotion
        score += text.count('!') * 2
        
        # Short punchy lines score higher (hook-like)
        word_count = len(text.split())
        if word_count <= 8:
            score += 2
        
        # ALL CAPS words = emphasis
        original = sub.text.replace('\n', ' ')
        caps_words = len([w for w in original.split() if w.isupper() and len(w) > 1])
        score += caps_words * 2
        
        scored_segments.append({
            "start": sub.start.ordinal / 1000,  # seconds
            "end": sub.end.ordinal / 1000,
            "text": sub.text.replace('\n', ' '),
            "score": score
        })
    
    return scored_segments

def find_clip_windows(segments, clip_duration=30, top_n=5):
    """Find the best clip windows based on engagement scores"""
    if not segments:
        return []
    
    total_duration = segments[-1]["end"]
    windows = []
    
    # Sliding window
    step = 5  # 5 second steps
    for start in range(0, int(total_duration - clip_duration), step):
        end = start + clip_duration
        window_score = sum(
            s["score"] for s in segments
            if s["start"] >= start and s["end"] <= end
        )
        windows.append({
            "start": start,
            "end": end,
            "score": window_score
        })
    
    # Sort by score, pick top N non-overlapping
    windows.sort(key=lambda x: x["score"], reverse=True)
    
    selected = []
    for w in windows:
        # Check overlap with already selected
        overlap = False
        for s in selected:
            if not (w["end"] <= s["start"] or w["start"] >= s["end"]):
                overlap = True
                break
        if not overlap:
            selected.append(w)
        if len(selected) >= top_n:
            break
    
    # Sort by time order
    selected.sort(key=lambda x: x["start"])
    return selected

def cut_clip(input_video: str, start: float, end: float, output_path: str):
    """Cut a clip from video using ffmpeg"""
    duration = end - start
    cmd = [
        "ffmpeg", "-y", "-ss", str(start), "-i", input_video,
        "-t", str(duration), "-c:v", "libx264", "-c:a", "aac",
        "-preset", "fast", "-crf", "23", output_path
    ]
    subprocess.run(cmd, capture_output=True, timeout=120)

@app.post("/api/clip/analyze")
async def analyze_for_clips(
    video: UploadFile = File(...),
    subtitle: UploadFile = File(None),
    clip_duration: int = Form(30),
    num_clips: int = Form(5)
):
    """Upload video + optional SRT, get engagement-scored clip suggestions"""
    clip_id = str(uuid.uuid4())[:8]
    clip_dir = os.path.join(OUTPUT_DIR, "clips", clip_id)
    os.makedirs(clip_dir, exist_ok=True)
    
    # Save video
    video_path = os.path.join(clip_dir, f"source_{video.filename}")
    with open(video_path, "wb") as f:
        content = await video.read()
        f.write(content)
    
    # Handle subtitle
    srt_path = None
    if subtitle:
        srt_path = os.path.join(clip_dir, subtitle.filename)
        with open(srt_path, "wb") as f:
            srt_content = await subtitle.read()
            f.write(srt_content)
    else:
        # Auto-generate subtitle using whisper if available, else ffmpeg
        srt_path = os.path.join(clip_dir, "auto_subtitle.srt")
        # Try to extract embedded subtitles first
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", video_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Generate subtitles via speech-to-text (whisper)
        try:
            whisper_cmd = ["whisper", video_path, "--output_format", "srt", 
                         "--output_dir", clip_dir, "--language", "id", "--model", "base"]
            subprocess.run(whisper_cmd, capture_output=True, timeout=300)
            # Find generated srt
            for f_name in os.listdir(clip_dir):
                if f_name.endswith('.srt') and f_name != "auto_subtitle.srt":
                    os.rename(os.path.join(clip_dir, f_name), srt_path)
                    break
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # Whisper not available - return video info only
            pass
    
    if not srt_path or not os.path.exists(srt_path):
        # Can't analyze without subtitles - return video duration info
        probe_cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                    "-of", "json", video_path]
        probe = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = json.loads(probe.stdout).get("format", {}).get("duration", "0")
        return {
            "status": "ok",
            "message": "No subtitle available. Upload SRT file for engagement analysis.",
            "video_duration": float(duration),
            "clip_id": clip_id
        }
    
    # Analyze engagement
    segments = analyze_srt_engagement(srt_path)
    clips = find_clip_windows(segments, clip_duration=clip_duration, top_n=num_clips)
    
    # Add preview text for each clip
    for clip in clips:
        clip_texts = [s["text"] for s in segments 
                     if s["start"] >= clip["start"] and s["end"] <= clip["end"]]
        clip["preview"] = " ".join(clip_texts[:3]) + "..."
    
    return {
        "status": "ok",
        "clip_id": clip_id,
        "video_path": video_path,
        "total_segments": len(segments),
        "suggested_clips": clips
    }

@app.post("/api/clip/cut")
async def cut_clips(request: Request):
    """Cut selected clips from analyzed video"""
    body = await request.json()
    clip_id = body.get("clip_id")
    clips = body.get("clips", [])  # [{start, end}]
    
    clip_dir = os.path.join(OUTPUT_DIR, "clips", clip_id)
    if not os.path.exists(clip_dir):
        return {"status": "error", "message": "Clip ID not found"}
    
    # Find source video
    video_path = None
    for f_name in os.listdir(clip_dir):
        if f_name.startswith("source_"):
            video_path = os.path.join(clip_dir, f_name)
            break
    
    if not video_path:
        return {"status": "error", "message": "Source video not found"}
    
    results = []
    for i, clip in enumerate(clips):
        output_name = f"clip_{i+1}_{int(clip['start'])}s-{int(clip['end'])}s.mp4"
        output_path = os.path.join(clip_dir, output_name)
        
        try:
            cut_clip(video_path, clip["start"], clip["end"], output_path)
            results.append({
                "clip_num": i + 1,
                "start": clip["start"],
                "end": clip["end"],
                "file": f"/outputs/clips/{clip_id}/{output_name}",
                "status": "ok"
            })
        except Exception as e:
            results.append({
                "clip_num": i + 1,
                "status": "error",
                "error": str(e)
            })
    
    return {"status": "ok", "clips": results}

# ============ AUTO-SUBTITLE ============

@app.post("/api/subtitle/generate")
async def api_generate_subtitle(video: UploadFile = File(...), language: str = Form("id")):
    """Upload video, generate SRT subtitle via Whisper"""
    from features import generate_subtitle
    
    sub_id = str(uuid.uuid4())[:8]
    sub_dir = os.path.join(OUTPUT_DIR, "subtitles", sub_id)
    os.makedirs(sub_dir, exist_ok=True)
    
    video_path = os.path.join(sub_dir, video.filename)
    with open(video_path, "wb") as f:
        content = await video.read()
        f.write(content)
    
    try:
        srt_path = generate_subtitle(video_path, language=language)
        if srt_path and os.path.exists(srt_path):
            with open(srt_path, 'r') as f:
                srt_content = f.read()
            return {
                "status": "ok",
                "srt_content": srt_content,
                "download": f"/outputs/subtitles/{sub_id}/{os.path.basename(srt_path)}"
            }
        else:
            return {"status": "error", "message": "Whisper failed to generate subtitle"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============ VIDEO TO SHORTS ============

@app.post("/api/shorts/convert")
async def api_convert_shorts(video: UploadFile = File(...), position: str = Form("center")):
    """Convert landscape video to 9:16 shorts format"""
    from features import reframe_to_shorts
    
    short_id = str(uuid.uuid4())[:8]
    short_dir = os.path.join(OUTPUT_DIR, "shorts", short_id)
    os.makedirs(short_dir, exist_ok=True)
    
    video_path = os.path.join(short_dir, f"source_{video.filename}")
    with open(video_path, "wb") as f:
        content = await video.read()
        f.write(content)
    
    output_path = os.path.join(short_dir, f"short_9x16_{video.filename}")
    
    try:
        result = reframe_to_shorts(video_path, output_path, position=position)
        if result:
            return {
                "status": "ok",
                "download": f"/outputs/shorts/{short_id}/{os.path.basename(output_path)}"
            }
        else:
            return {"status": "error", "message": "Conversion failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============ FACELESS VIDEO ============

@app.post("/api/faceless/generate")
async def api_generate_faceless(request: Request):
    """Generate faceless video from script text"""
    from features import generate_tts, create_subtitle_srt, get_audio_duration, create_faceless_video
    
    body = await request.json()
    script = body.get("script", "")
    voice = body.get("voice", "id-ID-ArdiNeural")
    bg_color = body.get("bg_color", "#1a1a2e")
    
    if not script:
        return {"status": "error", "message": "Script is required"}
    
    vid_id = str(uuid.uuid4())[:8]
    vid_dir = os.path.join(OUTPUT_DIR, "faceless", vid_id)
    os.makedirs(vid_dir, exist_ok=True)
    
    audio_path = os.path.join(vid_dir, "voice.mp3")
    srt_path = os.path.join(vid_dir, "subtitle.srt")
    output_path = os.path.join(vid_dir, "faceless_video.mp4")
    
    try:
        # Generate TTS
        await generate_tts(script, audio_path, voice=voice)
        
        # Get duration and create subtitle
        duration = get_audio_duration(audio_path)
        create_subtitle_srt(script, duration, srt_path)
        
        # Create video
        result = create_faceless_video(audio_path, srt_path, output_path, bg_color=bg_color)
        
        if result:
            return {
                "status": "ok",
                "duration": round(duration, 1),
                "download": f"/outputs/faceless/{vid_id}/faceless_video.mp4"
            }
        else:
            return {"status": "error", "message": "Video creation failed"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ============ TREND TRACKER ============

@app.get("/api/trends/youtube")
async def api_youtube_trends():
    """Get YouTube trending topics"""
    from features import scrape_youtube_trending
    topics = await scrape_youtube_trending()
    return {"status": "ok", "trends": topics}

# ============ TEMPLATE LIBRARY ============

@app.get("/api/templates")
async def api_list_templates():
    from features import load_templates
    return {"status": "ok", "templates": load_templates()}

@app.post("/api/templates")
async def api_save_template(request: Request):
    from features import save_template
    body = await request.json()
    template = save_template(body)
    return {"status": "ok", "template": template}

@app.delete("/api/templates/{template_id}")
async def api_delete_template(template_id: str):
    from features import delete_template
    delete_template(template_id)
    return {"status": "ok"}

# ============ A/B TITLE TESTER ============

@app.post("/api/ab-title/generate")
async def api_ab_title(request: Request):
    """Generate multiple title variations with CTR scoring"""
    body = await request.json()
    topic = body.get("topic", "")
    count = body.get("count", 5)
    
    system = f"""Kamu adalah YouTube SEO expert. Buat {count} variasi judul untuk video.
Untuk setiap judul:
- Judul (max 60 chars)
- CTR Score (1-10, berdasarkan clickability)
- Alasan kenapa score segitu (1 kalimat)

Kriteria CTR tinggi: curiosity gap, angka spesifik, emotional trigger, power words.
Format: numbered list, setiap item ada Judul | Score | Alasan."""

    content = await ai_chat(system, f"Topic: {topic}")
    return {"status": "ok", "titles": content}

# ============ BULK GENERATOR ============

@app.post("/api/bulk/generate")
async def api_bulk_generate(request: Request):
    """Batch generate multiple scripts/captions"""
    body = await request.json()
    gen_type = body.get("type", "caption")  # caption, script, hooks
    topics = body.get("topics", [])
    platform = body.get("platform", "instagram")
    
    if not topics:
        return {"status": "error", "message": "Provide list of topics"}
    
    results = []
    for topic in topics[:20]:  # Max 20
        try:
            if gen_type == "caption":
                system = f"Buat caption {platform} singkat dan engaging untuk: {topic}. Include 5 hashtag."
            elif gen_type == "script":
                system = f"Buat script 60 detik untuk {platform} tentang: {topic}. Format: HOOK - BODY - CTA."
            else:
                system = f"Buat 3 hook ideas untuk: {topic}"
            
            content = await ai_chat("Kamu content creator expert.", system)
            results.append({"topic": topic, "content": content, "status": "ok"})
        except Exception as e:
            results.append({"topic": topic, "error": str(e), "status": "error"})
    
    return {"status": "ok", "results": results}

# ============ EXPORT ============

@app.post("/api/export/csv")
async def api_export_csv(request: Request):
    """Export content calendar to CSV"""
    conn = get_db()
    rows = conn.execute("SELECT * FROM schedules ORDER BY scheduled_at ASC").fetchall()
    conn.close()
    
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Title", "Platform", "Content", "Scheduled At", "Status"])
    for r in rows:
        writer.writerow([r["title"], r["platform"], r["content"], r["scheduled_at"], r["status"]])
    
    csv_path = os.path.join(OUTPUT_DIR, "export_calendar.csv")
    with open(csv_path, 'w') as f:
        f.write(output.getvalue())
    
    return FileResponse(csv_path, filename="content_calendar.csv", media_type="text/csv")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
