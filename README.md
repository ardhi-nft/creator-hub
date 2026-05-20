# 🎬 Creator Hub

Content Creator Toolkit — AI-powered tools untuk bikin konten lebih cepat dan efisien.

## Features

### ✍️ Writing & AI Tools
| Feature | Deskripsi |
|---------|-----------|
| 📝 Script Generator | Generate script video (YouTube, TikTok, Reels, Podcast) |
| 💬 Caption & Hashtag | Auto-generate caption + hashtag per platform |
| 🎣 Hook Ideas | Bikin opening lines yang stop scrolling |
| 🖼️ Thumbnail Ideas | Konsep thumbnail high-CTR |
| 💡 Content Ideas | Ide konten berdasarkan niche & platform |
| 🔍 SEO Optimizer | Title, description, tags yang SEO-friendly |
| 🎯 A/B Title Tester | Multiple title variations + CTR scoring |
| ⚡ Bulk Generator | Batch generate caption/script/hooks sekaligus |

### 🎥 Video Tools
| Feature | Deskripsi |
|---------|-----------|
| ✂️ Auto-Clip | Detect bagian paling engaging, auto-cut jadi clips |
| 🗣️ Auto-Subtitle | Generate subtitle (SRT) dari video via Whisper AI |
| 📱 Video to Shorts | Convert landscape → 9:16 vertical (Shorts/Reels) |
| 🎭 Faceless Video | Script → TTS + subtitle overlay → video jadi |

### 📋 Productivity
| Feature | Deskripsi |
|---------|-----------|
| 📈 Trend Tracker | YouTube trending topics Indonesia |
| 📋 Template Library | Save & reuse caption/script templates |
| 📅 Content Calendar | Schedule + manage content plan |
| 📚 History | Riwayat semua generated content |
| ⬇️ Export CSV | Export calendar ke spreadsheet |

## Tech Stack

- **Backend:** Python + FastAPI
- **Frontend:** Vanilla HTML/CSS/JS (dark theme)
- **AI:** OpenAI-compatible API (via proxy/router)
- **Video:** FFmpeg + Whisper + edge-tts
- **Database:** SQLite
- **Deployment:** Systemd service

## Quick Start

### Prerequisites

- Python 3.10+
- FFmpeg
- (Optional) NVIDIA GPU for faster Whisper

### Installation

```bash
# Clone
git clone https://github.com/ardhi-nft/creator-hub.git
cd creator-hub

# Install dependencies
pip install -r requirements.txt

# Install Whisper (for auto-subtitle)
pip install openai-whisper

# Install Playwright browsers (optional, for future features)
# python -m playwright install chromium

# Run
python app.py
```

Server runs at `http://localhost:8002`

### Environment Variables

```bash
AI_API_KEY=your-api-key-here  # OpenAI-compatible API key
```

Set via environment or in systemd service file.

### Systemd Service (Production)

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
Environment=AI_API_KEY=your-key

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable creator-hub
sudo systemctl start creator-hub
```

## API Endpoints

### Writing & AI
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/script/generate` | Generate video script |
| POST | `/api/caption/generate` | Generate caption + hashtags |
| POST | `/api/hooks/generate` | Generate hook ideas |
| POST | `/api/thumbnail/ideas` | Generate thumbnail concepts |
| POST | `/api/ideas/generate` | Generate content ideas |
| POST | `/api/seo/generate` | Generate SEO title/desc/tags |
| POST | `/api/ab-title/generate` | A/B title variations |
| POST | `/api/bulk/generate` | Batch generate content |

### Video Tools
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/clip/analyze` | Analyze video for best clips |
| POST | `/api/clip/cut` | Cut selected clips |
| POST | `/api/subtitle/generate` | Generate SRT from video |
| POST | `/api/shorts/convert` | Convert to 9:16 format |
| POST | `/api/faceless/generate` | Generate faceless video |

### Productivity
| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/api/trends/youtube` | Get trending topics |
| GET/POST | `/api/templates` | List/save templates |
| DELETE | `/api/templates/{id}` | Delete template |
| POST | `/api/schedule/create` | Add to calendar |
| GET | `/api/schedule/list` | List schedules |
| POST | `/api/export/csv` | Export calendar CSV |

## Project Structure

```
creator-hub/
├── app.py              # Main FastAPI application + routes
├── features.py         # Feature modules (subtitle, shorts, faceless, etc)
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/style.css   # Dark theme stylesheet
│   └── js/app.js       # Frontend JavaScript
├── templates/
│   └── index.html      # Single-page app HTML
├── data/               # SQLite database (gitignored)
└── outputs/            # Generated files (gitignored)
    ├── clips/
    ├── subtitles/
    ├── shorts/
    └── faceless/
```

## Notes

- **Video tools** (subtitle, shorts, faceless, clip) work without API key
- **AI writing tools** require an OpenAI-compatible API key
- Whisper runs on CPU by default (slower). GPU recommended for large videos
- FFmpeg is required for all video processing features

## License

MIT
