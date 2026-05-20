# 🎬 Creator Hub

AI-powered Content Creator Toolkit — semua tools yang dibutuhin content creator dalam satu dashboard.

## ✨ Demo

Live: `http://your-server:8002`  
Default password: `creator2026`

---

## 🚀 Features

### ✍️ Writing & AI Tools (butuh API key)
| Feature | Deskripsi |
|---------|-----------|
| 📝 Script Generator | Generate script video untuk YouTube, TikTok, Reels, Podcast |
| 💬 Caption & Hashtag | Auto-generate caption + hashtag sesuai platform & tone |
| 🎣 Hook Ideas | Opening lines yang bikin orang stop scrolling |
| 🖼️ Thumbnail Ideas | Konsep thumbnail high-CTR (visual, text, color scheme) |
| 💡 Content Ideas | Ide konten berdasarkan niche, platform, difficulty level |
| 🔍 SEO Optimizer | Title, description, tags yang SEO-friendly |
| 🎯 A/B Title Tester | Multiple title variations + CTR scoring |
| ⚡ Bulk Generator | Batch generate caption/script/hooks untuk banyak topik sekaligus |

### 🎥 Video Tools (tanpa API key)
| Feature | Deskripsi |
|---------|-----------|
| ✂️ Auto-Clip | Detect bagian paling engaging dari video, auto-cut jadi clips |
| 🗣️ Auto-Subtitle | Generate subtitle (SRT) dari video via Whisper AI |
| 📱 Video to Shorts | Convert landscape → 9:16 vertical (Shorts/Reels/TikTok) |
| 🎭 Faceless Video | Script → TTS voice + gradient/solid bg + subtitle → video jadi |

### 🚀 Auto-Pipeline
| Feature | Deskripsi |
|---------|-----------|
| Upload → Edit → Post | One-click: subtitle + reframe + clip + post ke Telegram |
| Preview | Preview hasil video sebelum posting |
| Telegram Integration | Auto-post ke channel/group Telegram |

### 📋 Productivity
| Feature | Deskripsi |
|---------|-----------|
| 📈 Trend Tracker | YouTube trending topics Indonesia |
| 📋 Template Library | Save & reuse caption/script templates dengan variables |
| 📅 Content Calendar | Schedule + manage content plan |
| ⬇️ Export CSV | Export calendar ke spreadsheet |
| 📚 History | Riwayat semua generated content |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+ / FastAPI
- **Frontend:** Vanilla HTML/CSS/JS (dark theme, responsive)
- **AI:** OpenAI-compatible API (GPT, Claude, dll via proxy)
- **Video Processing:** FFmpeg
- **Speech-to-Text:** OpenAI Whisper
- **Text-to-Speech:** Edge-TTS (Microsoft)
- **Database:** SQLite
- **Auth:** Session-based password protection

---

## 📦 Installation

### Prerequisites

```bash
# Required
python3 >= 3.10
ffmpeg

# Optional (for GPU-accelerated Whisper)
nvidia-driver + CUDA
```

### Setup

```bash
# 1. Clone repo
git clone https://github.com/ardhi-nft/creator-hub.git
cd creator-hub

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run development server
python app.py
```

Server berjalan di `http://localhost:8002`

### Production (Systemd)

```bash
# 1. Create service file
sudo nano /etc/systemd/system/creator-hub.service
```

```ini
[Unit]
Description=Creator Hub
After=network.target

[Service]
Type=simple
WorkingDirectory=/path/to/creator-hub
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8002
Restart=always
RestartSec=3
Environment=AI_API_KEY=your-openai-compatible-key
Environment=CREATOR_HUB_PASSWORD=your-password
Environment=TELEGRAM_BOT_TOKEN=your-bot-token
Environment=TELEGRAM_CHAT_ID=your-chat-id

[Install]
WantedBy=multi-user.target
```

```bash
# 2. Enable & start
sudo systemctl daemon-reload
sudo systemctl enable creator-hub
sudo systemctl start creator-hub

# 3. Check status
sudo systemctl status creator-hub
```

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Default | Deskripsi |
|----------|----------|---------|-----------|
| `AI_API_KEY` | For AI features | - | OpenAI-compatible API key |
| `CREATOR_HUB_PASSWORD` | No | `creator2026` | Login password |
| `TELEGRAM_BOT_TOKEN` | For Telegram | - | Bot token dari @BotFather |
| `TELEGRAM_CHAT_ID` | For Telegram | - | Channel/group/chat ID tujuan |

### Setup Telegram Bot (untuk Auto-Pipeline posting)

1. Chat [@BotFather](https://t.me/BotFather) di Telegram
2. `/newbot` → ikuti instruksi → dapat **Bot Token**
3. Add bot ke channel/group sebagai admin
4. Dapatkan Chat ID:
   - Untuk channel: forward pesan dari channel ke [@userinfobot](https://t.me/userinfobot)
   - Untuk group: invite [@RawDataBot](https://t.me/RawDataBot) ke group, lihat chat ID
   - Untuk private chat: chat bot, lalu buka `https://api.telegram.org/bot<TOKEN>/getUpdates`
5. Set environment variables di systemd service
6. Restart service: `sudo systemctl restart creator-hub`

### Setup AI API Key

Bisa pakai:
- **OpenAI** langsung: `sk-...`
- **AI Router/Proxy** (recommended): local proxy yang forward ke multiple providers
- **Any OpenAI-compatible API**: Groq, Together, Anthropic via proxy, dll

Set di environment: `AI_API_KEY=your-key`

---

## 📖 Usage Guide

### 1. Login
Buka `http://your-server:8002`, masukkan password.

### 2. Generate Script
- Klik **📝 Script** di sidebar
- Isi topic, pilih platform & style
- Klik "Generate Script" → hasil muncul dengan tombol Copy

### 3. Auto-Pipeline (Upload → Edit → Post)
- Klik **🚀 Pipeline** di sidebar
- Upload video file
- Pilih processing options:
  - ✅ Auto-Subtitle: generate & burn subtitle ke video
  - ✅ Reframe 9:16: convert ke format vertical
  - ☐ Auto-Clip: potong bagian paling engaging
  - ☐ Post Telegram: langsung kirim ke channel
- Klik "Run Pipeline" → preview hasil → download

### 4. Faceless Video
- Klik **🎭 Faceless** di sidebar
- Tulis script narasi
- Pilih voice (ID/EN, Male/Female)
- Pilih background (gradient/solid)
- Klik "Generate" → video siap download

### 5. Auto-Clip
- Klik **✂️ Auto-Clip** di sidebar
- Upload video + SRT subtitle
- Pilih durasi clip & jumlah
- Sistem analisis engagement score per segment
- Pilih clips yang mau di-cut → download

### 6. Bulk Generator
- Klik **⚡ Bulk** di sidebar
- Tulis banyak topik (satu per baris)
- Pilih type (caption/script/hooks) & platform
- Generate semua sekaligus

---

## 🔌 API Reference

### Authentication
Semua API endpoints (kecuali `/api/login`) memerlukan session cookie dari login.

```bash
# Login
curl -X POST http://localhost:8002/api/login \
  -H "Content-Type: application/json" \
  -d '{"password": "creator2026"}'
```

### Writing & AI
```bash
# Generate Script
POST /api/script/generate
Body: {"topic": "...", "platform": "youtube", "style": "informative", "duration": "60"}

# Generate Caption
POST /api/caption/generate
Body: {"topic": "...", "platform": "instagram", "tone": "casual"}

# Hook Ideas
POST /api/hooks/generate
Body: {"topic": "...", "count": 5}

# Thumbnail Ideas
POST /api/thumbnail/ideas
Body: {"topic": "..."}

# Content Ideas
POST /api/ideas/generate
Body: {"niche": "...", "platform": "youtube", "count": 10}

# SEO Optimizer
POST /api/seo/generate
Body: {"topic": "...", "platform": "youtube"}

# A/B Title
POST /api/ab-title/generate
Body: {"topic": "...", "count": 5}

# Bulk Generate
POST /api/bulk/generate
Body: {"type": "caption", "platform": "instagram", "topics": ["topic1", "topic2"]}
```

### Video Tools
```bash
# Auto-Subtitle (multipart form)
POST /api/subtitle/generate
Form: video=@file.mp4, language=id

# Video to Shorts (multipart form)
POST /api/shorts/convert
Form: video=@file.mp4, position=center

# Faceless Video
POST /api/faceless/generate
Body: {"script": "...", "voice": "id-ID-ArdiNeural", "bg_color": "gradient_blue", "bg_style": "gradient"}

# Auto-Clip Analyze (multipart form)
POST /api/clip/analyze
Form: video=@file.mp4, subtitle=@file.srt, clip_duration=30, num_clips=5

# Cut Clips
POST /api/clip/cut
Body: {"clip_id": "abc123", "clips": [{"start": 10, "end": 40}]}

# Auto-Pipeline (multipart form)
POST /api/pipeline/run
Form: video=@file.mp4, add_subtitle=true, reframe_shorts=true, auto_clip=false, post_telegram=false, caption="..."
```

### Productivity
```bash
# YouTube Trends
GET /api/trends/youtube

# Templates CRUD
GET /api/templates
POST /api/templates  Body: {"name": "...", "category": "caption", "content": "..."}
DELETE /api/templates/{id}

# Schedule
POST /api/schedule/create  Body: {"title": "...", "platform": "youtube", "content": "...", "scheduled_at": "2026-01-01T10:00"}
GET /api/schedule/list
DELETE /api/schedule/{id}

# Export
POST /api/export/csv
```

---

## 📁 Project Structure

```
creator-hub/
├── app.py                 # Main FastAPI app + all API routes
├── features.py            # Video processing modules
├── requirements.txt       # Python dependencies
├── .gitignore
├── README.md
├── templates/
│   ├── index.html         # Main dashboard (SPA)
│   └── login.html         # Login page
├── static/
│   ├── css/style.css      # Dark theme styles
│   └── js/app.js          # Frontend logic
├── data/                  # SQLite DB + templates (gitignored)
└── outputs/               # Generated files (gitignored)
    ├── clips/
    ├── subtitles/
    ├── shorts/
    ├── faceless/
    └── pipeline/
```

---

## 🔒 Security Notes

- Password-protected access (session-based)
- Runs on private server, not exposed to public internet by default
- API key stored in environment variable, not in code
- Output files auto-generated with UUID, not guessable

---

## 📝 Changelog

### v2.0 (2026-05-20)
- Added password authentication
- Added Auto-Pipeline (upload → edit → post Telegram)
- Added Faceless Video with gradient backgrounds
- Added A/B Title Tester
- Added Bulk Generator
- Added Template Library
- Added Trend Tracker
- Added Export CSV
- Added Video to Shorts (9:16 reframe)
- Added Auto-Subtitle (Whisper)
- Added Auto-Clip (engagement scoring)

### v1.0 (2026-05-20)
- Initial release
- Script, Caption, Hooks, Thumbnail, Ideas, SEO generators
- Content Calendar
- Dark theme UI

---

## License

MIT
