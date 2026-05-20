"""Additional features for Creator Hub"""

import os
import json
import uuid
import subprocess
import asyncio
import re
import random
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# ============ 1. AUTO-SUBTITLE (WHISPER) ============

def generate_subtitle(video_path: str, language: str = "id", model: str = "base"):
    """Generate SRT subtitle from video using Whisper"""
    output_dir = os.path.dirname(video_path)
    base_name = os.path.splitext(os.path.basename(video_path))[0]
    
    cmd = [
        "whisper", video_path,
        "--output_format", "srt",
        "--output_dir", output_dir,
        "--language", language,
        "--model", model
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    
    # Find generated SRT
    srt_path = os.path.join(output_dir, f"{base_name}.srt")
    if os.path.exists(srt_path):
        return srt_path
    
    # Try alternative naming
    for f in os.listdir(output_dir):
        if f.endswith('.srt'):
            return os.path.join(output_dir, f)
    
    return None


# ============ 2. VIDEO TO SHORTS (REFRAME) ============

def get_video_info(video_path: str):
    """Get video dimensions and duration"""
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_streams", "-show_format", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    
    video_stream = next((s for s in data.get("streams", []) if s["codec_type"] == "video"), None)
    if not video_stream:
        return None
    
    return {
        "width": int(video_stream["width"]),
        "height": int(video_stream["height"]),
        "duration": float(data.get("format", {}).get("duration", 0)),
        "fps": eval(video_stream.get("r_frame_rate", "30/1"))
    }

def reframe_to_shorts(video_path: str, output_path: str, position: str = "center"):
    """Convert landscape video to 9:16 vertical (shorts/reels format)"""
    info = get_video_info(video_path)
    if not info:
        return None
    
    src_w, src_h = info["width"], info["height"]
    
    # Target 9:16 ratio
    target_w = 1080
    target_h = 1920
    
    # Calculate crop area from source
    # Scale height to match, then crop width
    if src_w / src_h > 9/16:
        # Wider than 9:16 - crop sides
        crop_h = src_h
        crop_w = int(src_h * 9 / 16)
        
        if position == "left":
            x_offset = 0
        elif position == "right":
            x_offset = src_w - crop_w
        else:  # center
            x_offset = (src_w - crop_w) // 2
        
        crop_filter = f"crop={crop_w}:{crop_h}:{x_offset}:0,scale={target_w}:{target_h}"
    else:
        # Taller or equal - crop top/bottom
        crop_w = src_w
        crop_h = int(src_w * 16 / 9)
        y_offset = (src_h - crop_h) // 2
        crop_filter = f"crop={crop_w}:{crop_h}:0:{y_offset},scale={target_w}:{target_h}"
    
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", crop_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        output_path
    ]
    
    subprocess.run(cmd, capture_output=True, timeout=300)
    return output_path if os.path.exists(output_path) else None


# ============ 3. FACELESS VIDEO GENERATOR ============

async def generate_tts(text: str, output_path: str, voice: str = "id-ID-ArdiNeural"):
    """Generate TTS audio using edge-tts"""
    import edge_tts
    
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)
    return output_path

def create_subtitle_srt(text: str, audio_duration: float, output_path: str):
    """Create simple SRT from text, splitting into chunks"""
    words = text.split()
    chunk_size = 8  # words per subtitle line
    chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
    
    time_per_chunk = audio_duration / len(chunks) if chunks else 1
    
    srt_content = ""
    for i, chunk in enumerate(chunks):
        start_time = i * time_per_chunk
        end_time = (i + 1) * time_per_chunk
        
        start_str = format_srt_time(start_time)
        end_str = format_srt_time(end_time)
        
        srt_content += f"{i+1}\n{start_str} --> {end_str}\n{chunk}\n\n"
    
    with open(output_path, 'w') as f:
        f.write(srt_content)
    
    return output_path

def format_srt_time(seconds: float) -> str:
    """Format seconds to SRT timestamp"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def get_audio_duration(audio_path: str) -> float:
    """Get audio file duration"""
    cmd = ["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "json", audio_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 0))

def create_faceless_video(audio_path: str, srt_path: str, output_path: str, 
                          bg_color: str = "#1a1a2e", text_color: str = "white",
                          bg_style: str = "solid", images: list = None):
    """Create video with background + subtitle overlay from audio"""
    duration = get_audio_duration(audio_path)
    
    # Background options
    if bg_style == "gradient" or bg_color.startswith("gradient"):
        # Gradient background (dark blue to purple)
        gradients = {
            "gradient_blue": "color=c=#0f0c29:s=1080x1920:d={d}[bg1];color=c=#302b63:s=1080x1920:d={d}[bg2];[bg1][bg2]blend=all_mode=overlay:all_opacity=0.5",
            "gradient_purple": "color=c=#1a0533:s=1080x1920:d={d}[bg1];color=c=#4a0e8f:s=1080x1920:d={d}[bg2];[bg1][bg2]blend=all_mode=overlay:all_opacity=0.5",
            "gradient_dark": "color=c=#0f0f0f:s=1080x1920:d={d}[bg1];color=c=#1a1a2e:s=1080x1920:d={d}[bg2];[bg1][bg2]blend=all_mode=overlay:all_opacity=0.5",
        }
        bg_filter = gradients.get(bg_color, gradients["gradient_blue"]).format(d=duration)
        input_args = ["-f", "lavfi", "-i", bg_filter]
    elif bg_style == "slideshow" and images:
        # Image slideshow background
        img_duration = duration / len(images) if images else duration
        concat_file = os.path.join(os.path.dirname(output_path), "concat.txt")
        with open(concat_file, 'w') as f:
            for img in images:
                f.write(f"file '{img}'\nduration {img_duration}\n")
            f.write(f"file '{images[-1]}'\n")  # last frame hold
        input_args = ["-f", "concat", "-safe", "0", "-i", concat_file]
    else:
        # Solid color
        input_args = ["-f", "lavfi", "-i", f"color=c={bg_color}:s=1080x1920:d={duration}"]
    
    # Subtitle filter
    subtitle_filter = (
        f"subtitles={srt_path}:force_style='"
        f"FontName=Arial,FontSize=24,PrimaryColour=&H00FFFFFF,"
        f"OutlineColour=&H00000000,Outline=2,Bold=1,Alignment=2,MarginV=80'"
    )
    
    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-i", audio_path,
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,{subtitle_filter}",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", output_path
    ]
    
    subprocess.run(cmd, capture_output=True, timeout=300)
    return output_path if os.path.exists(output_path) else None


# ============ 4. TREND TRACKER ============

async def scrape_youtube_trending(region: str = "ID"):
    """Get trending topics from YouTube (via RSS)"""
    import httpx
    
    url = f"https://www.youtube.com/feed/trending"
    rss_url = f"https://www.youtube.com/feeds/videos.xml?chart=most_popular&regionCode={region}"
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(rss_url)
            if resp.status_code == 200:
                titles = re.findall(r'<title>(.*?)</title>', resp.text)
                return titles[1:21]
    except:
        pass
    
    return []

async def scrape_twitter_trending():
    """Get trending topics (placeholder - needs API)"""
    return []


# ============ 5. TEMPLATE LIBRARY ============

TEMPLATES_FILE = os.path.join(BASE_DIR, "data", "templates.json")

def load_templates():
    """Load saved templates"""
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_template(template: dict):
    """Save a new template"""
    templates = load_templates()
    template["id"] = str(uuid.uuid4())[:8]
    template["created_at"] = datetime.now().isoformat()
    templates.append(template)
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)
    return template

def delete_template(template_id: str):
    """Delete a template"""
    templates = load_templates()
    templates = [t for t in templates if t.get("id") != template_id]
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)


# ============ 7. BULK GENERATOR ============

async def bulk_generate(ai_func, prompts: list):
    """Generate multiple items concurrently (max 3 at a time)"""
    import asyncio
    
    semaphore = asyncio.Semaphore(3)
    results = []
    
    async def limited_call(prompt):
        async with semaphore:
            return await ai_func(prompt)
    
    tasks = [limited_call(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
