// Creator Hub - Frontend JS

// Navigation
document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const page = link.dataset.page;
        
        document.querySelectorAll('.nav-links a').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(`page-${page}`).classList.add('active');
        
        if (page === 'schedule') loadSchedules();
        if (page === 'history') loadHistory('scripts');
        if (page === 'templates') loadTemplates();
    });
});

// Helper
async function apiCall(endpoint, data) {
    const resp = await fetch(endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    return resp.json();
}

function showResult(elementId, content, title = 'Result') {
    const el = document.getElementById(elementId);
    el.classList.remove('hidden');
    el.innerHTML = `<div class="result-wrapper"><button class="copy-btn" onclick="copyResult(this)">📋 Copy</button><h3>${title}</h3><div>${formatContent(content)}</div></div>`;
}

function formatContent(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/^### (.*$)/gm, '<h4 style="color:var(--accent);margin:12px 0 4px">$1</h4>')
        .replace(/^## (.*$)/gm, '<h3 style="color:var(--accent);margin:16px 0 8px">$1</h3>')
        .replace(/^# (.*$)/gm, '<h2 style="margin:16px 0 8px">$1</h2>')
        .replace(/^- (.*$)/gm, '• $1')
        .replace(/\n/g, '<br>');
}

function copyResult(btn) {
    const text = btn.parentElement.querySelector('div').innerText;
    navigator.clipboard.writeText(text);
    btn.textContent = '✅ Copied!';
    setTimeout(() => btn.textContent = '📋 Copy', 2000);
}

function setLoading(btn, loading) {
    if (loading) {
        btn.classList.add('loading');
        btn.disabled = true;
    } else {
        btn.classList.remove('loading');
        btn.disabled = false;
    }
}

// ============ SCRIPT ============
async function generateScript() {
    const btn = event.target;
    setLoading(btn, true);
    const data = {
        topic: document.getElementById('script-topic').value,
        platform: document.getElementById('script-platform').value,
        style: document.getElementById('script-style').value,
        duration: document.getElementById('script-duration').value
    };
    if (!data.topic) { setLoading(btn, false); return alert('Isi topic dulu'); }
    const result = await apiCall('/api/script/generate', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('script-result', result.script, '📝 Script');
    else showResult('script-result', 'Error: ' + (result.detail || 'Something went wrong'), '❌ Error');
}

// ============ CAPTION ============
async function generateCaption() {
    const btn = event.target;
    setLoading(btn, true);
    const data = {
        topic: document.getElementById('caption-topic').value,
        platform: document.getElementById('caption-platform').value,
        tone: document.getElementById('caption-tone').value
    };
    if (!data.topic) { setLoading(btn, false); return alert('Isi topic dulu'); }
    const result = await apiCall('/api/caption/generate', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('caption-result', result.caption, '💬 Caption & Hashtags');
}

// ============ HOOKS ============
async function generateHooks() {
    const btn = event.target;
    setLoading(btn, true);
    const data = {
        topic: document.getElementById('hooks-topic').value,
        count: parseInt(document.getElementById('hooks-count').value)
    };
    if (!data.topic) { setLoading(btn, false); return alert('Isi topic dulu'); }
    const result = await apiCall('/api/hooks/generate', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('hooks-result', result.hooks, '🎣 Hook Ideas');
}

// ============ THUMBNAIL ============
async function generateThumbnail() {
    const btn = event.target;
    setLoading(btn, true);
    const data = { topic: document.getElementById('thumb-topic').value };
    if (!data.topic) { setLoading(btn, false); return alert('Isi topic dulu'); }
    const result = await apiCall('/api/thumbnail/ideas', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('thumb-result', result.ideas, '🖼️ Thumbnail Concepts');
}

// ============ IDEAS ============
async function generateIdeas() {
    const btn = event.target;
    setLoading(btn, true);
    const data = {
        niche: document.getElementById('ideas-niche').value,
        platform: document.getElementById('ideas-platform').value,
        count: parseInt(document.getElementById('ideas-count').value)
    };
    if (!data.niche) { setLoading(btn, false); return alert('Isi niche dulu'); }
    const result = await apiCall('/api/ideas/generate', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('ideas-result', result.ideas, '💡 Content Ideas');
}

// ============ SEO ============
async function generateSEO() {
    const btn = event.target;
    setLoading(btn, true);
    const data = {
        topic: document.getElementById('seo-topic').value,
        platform: document.getElementById('seo-platform').value
    };
    if (!data.topic) { setLoading(btn, false); return alert('Isi topic dulu'); }
    const result = await apiCall('/api/seo/generate', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('seo-result', result.seo, '🔍 SEO Optimization');
}

// ============ A/B TITLE ============
async function generateABTitle() {
    const btn = event.target;
    setLoading(btn, true);
    const data = {
        topic: document.getElementById('ab-topic').value,
        count: parseInt(document.getElementById('ab-count').value)
    };
    if (!data.topic) { setLoading(btn, false); return alert('Isi topic dulu'); }
    const result = await apiCall('/api/ab-title/generate', data);
    setLoading(btn, false);
    if (result.status === 'ok') showResult('ab-result', result.titles, '🎯 Title Variations & CTR Score');
}

// ============ TRENDS ============
async function loadTrends() {
    const btn = event.target;
    setLoading(btn, true);
    const resp = await fetch('/api/trends/youtube');
    const data = await resp.json();
    setLoading(btn, false);
    
    const el = document.getElementById('trends-result');
    el.classList.remove('hidden');
    
    if (data.trends && data.trends.length > 0) {
        let html = '<h3>🔥 YouTube Trending Indonesia</h3>';
        html += data.trends.map((t, i) => `<div class="schedule-item"><span>${i+1}. ${t}</span></div>`).join('');
        el.innerHTML = html;
    } else {
        el.innerHTML = '<p style="color:var(--text-muted)">Tidak bisa load trends saat ini</p>';
    }
}

// ============ AUTO-CLIP ============
let currentClipId = null;

async function analyzeClips() {
    const btn = event.target;
    const videoFile = document.getElementById('clip-video').files[0];
    const subtitleFile = document.getElementById('clip-subtitle').files[0];
    if (!videoFile) return alert('Upload video dulu');
    
    setLoading(btn, true);
    const formData = new FormData();
    formData.append('video', videoFile);
    if (subtitleFile) formData.append('subtitle', subtitleFile);
    formData.append('clip_duration', document.getElementById('clip-duration').value);
    formData.append('num_clips', document.getElementById('clip-count').value);
    
    try {
        const resp = await fetch('/api/clip/analyze', { method: 'POST', body: formData });
        const data = await resp.json();
        setLoading(btn, false);
        
        if (data.status === 'ok' && data.suggested_clips) {
            currentClipId = data.clip_id;
            renderClipResults(data);
        } else {
            showResult('clip-result', data.message || 'Upload SRT file untuk analisis engagement', '⚠️ Info');
        }
    } catch (e) {
        setLoading(btn, false);
        showResult('clip-result', 'Error: ' + e.message, '❌ Error');
    }
}

function renderClipResults(data) {
    const el = document.getElementById('clip-result');
    el.classList.remove('hidden');
    let html = `<h3>✂️ ${data.suggested_clips.length} Best Clips Found</h3>`;
    html += `<p style="color:var(--text-muted);margin-bottom:16px">Analyzed ${data.total_segments} segments</p>`;
    
    data.suggested_clips.forEach((clip, i) => {
        const startMin = Math.floor(clip.start / 60);
        const startSec = Math.floor(clip.start % 60);
        const endMin = Math.floor(clip.end / 60);
        const endSec = Math.floor(clip.end % 60);
        html += `
            <div class="schedule-item" style="flex-direction:column;align-items:flex-start;gap:8px">
                <div style="display:flex;justify-content:space-between;width:100%;align-items:center">
                    <h4>Clip ${i+1} — ${startMin}:${String(startSec).padStart(2,'0')} → ${endMin}:${String(endSec).padStart(2,'0')}</h4>
                    <span class="badge">Score: ${clip.score}</span>
                </div>
                <span style="font-size:12px;color:var(--text-muted)">${clip.preview || ''}</span>
                <label style="font-size:12px;display:flex;align-items:center;gap:6px">
                    <input type="checkbox" class="clip-check" data-start="${clip.start}" data-end="${clip.end}" checked> Include
                </label>
            </div>`;
    });
    
    html += `<button class="btn-primary" style="margin-top:16px" onclick="cutSelectedClips()">Cut Selected Clips ✂️</button>`;
    html += `<div id="clip-cut-result" style="margin-top:16px"></div>`;
    el.innerHTML = html;
}

async function cutSelectedClips() {
    const btn = event.target;
    const checkboxes = document.querySelectorAll('.clip-check:checked');
    if (checkboxes.length === 0) return alert('Pilih minimal 1 clip');
    
    const clips = Array.from(checkboxes).map(cb => ({
        start: parseFloat(cb.dataset.start), end: parseFloat(cb.dataset.end)
    }));
    
    setLoading(btn, true);
    const resp = await fetch('/api/clip/cut', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ clip_id: currentClipId, clips })
    });
    const data = await resp.json();
    setLoading(btn, false);
    
    const resultEl = document.getElementById('clip-cut-result');
    if (data.status === 'ok') {
        let html = '<h3 style="color:var(--success);margin-bottom:12px">✅ Clips Ready!</h3>';
        data.clips.forEach(c => {
            if (c.status === 'ok') {
                html += `<div class="schedule-item">
                    <span>Clip ${c.clip_num} (${Math.floor(c.start)}s - ${Math.floor(c.end)}s)</span>
                    <a href="${c.file}" download style="color:var(--accent);text-decoration:none">⬇️ Download</a>
                </div>`;
            }
        });
        resultEl.innerHTML = html;
    }
}

// ============ SUBTITLE ============
async function generateSubtitle() {
    const btn = event.target;
    const videoFile = document.getElementById('sub-video').files[0];
    if (!videoFile) return alert('Upload video dulu');
    
    setLoading(btn, true);
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('language', document.getElementById('sub-language').value);
    
    try {
        const resp = await fetch('/api/subtitle/generate', { method: 'POST', body: formData });
        const data = await resp.json();
        setLoading(btn, false);
        
        if (data.status === 'ok') {
            const el = document.getElementById('sub-result');
            el.classList.remove('hidden');
            el.innerHTML = `
                <div class="result-wrapper">
                    <button class="copy-btn" onclick="copyResult(this)">📋 Copy</button>
                    <h3>🗣️ Subtitle Generated</h3>
                    <a href="${data.download}" download style="color:var(--accent);display:block;margin-bottom:12px">⬇️ Download SRT</a>
                    <pre style="white-space:pre-wrap;font-size:12px;max-height:400px;overflow-y:auto">${data.srt_content}</pre>
                </div>`;
        } else {
            showResult('sub-result', data.message || 'Failed', '❌ Error');
        }
    } catch (e) {
        setLoading(btn, false);
        showResult('sub-result', 'Error: ' + e.message, '❌ Error');
    }
}

// ============ SHORTS ============
async function convertShorts() {
    const btn = event.target;
    const videoFile = document.getElementById('shorts-video').files[0];
    if (!videoFile) return alert('Upload video dulu');
    
    setLoading(btn, true);
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('position', document.getElementById('shorts-position').value);
    
    try {
        const resp = await fetch('/api/shorts/convert', { method: 'POST', body: formData });
        const data = await resp.json();
        setLoading(btn, false);
        
        if (data.status === 'ok') {
            const el = document.getElementById('shorts-result');
            el.classList.remove('hidden');
            el.innerHTML = `
                <h3 style="color:var(--success)">✅ Converted to 9:16!</h3>
                <a href="${data.download}" download class="btn-primary" style="display:inline-block;margin-top:12px;text-decoration:none;text-align:center">⬇️ Download Shorts Video</a>`;
        } else {
            showResult('shorts-result', data.message || 'Failed', '❌ Error');
        }
    } catch (e) {
        setLoading(btn, false);
        showResult('shorts-result', 'Error: ' + e.message, '❌ Error');
    }
}

// ============ FACELESS VIDEO ============
async function generateFaceless() {
    const btn = event.target;
    const script = document.getElementById('faceless-script').value;
    if (!script) return alert('Tulis script dulu');
    
    setLoading(btn, true);
    const data = {
        script: script,
        voice: document.getElementById('faceless-voice').value,
        bg_color: document.getElementById('faceless-bg').value
    };
    
    try {
        const result = await apiCall('/api/faceless/generate', data);
        setLoading(btn, false);
        
        if (result.status === 'ok') {
            const el = document.getElementById('faceless-result');
            el.classList.remove('hidden');
            el.innerHTML = `
                <h3 style="color:var(--success)">✅ Video Generated! (${result.duration}s)</h3>
                <video controls style="width:100%;max-width:360px;margin:12px 0;border-radius:8px">
                    <source src="${result.download}" type="video/mp4">
                </video>
                <br><a href="${result.download}" download class="btn-primary" style="display:inline-block;margin-top:8px;text-decoration:none;text-align:center;width:auto;padding:10px 20px">⬇️ Download Video</a>`;
        } else {
            showResult('faceless-result', result.message || 'Failed', '❌ Error');
        }
    } catch (e) {
        setLoading(btn, false);
        showResult('faceless-result', 'Error: ' + e.message, '❌ Error');
    }
}

// ============ BULK GENERATOR ============
async function bulkGenerate() {
    const btn = event.target;
    const topicsRaw = document.getElementById('bulk-topics').value;
    if (!topicsRaw.trim()) return alert('Isi topics dulu');
    
    const topics = topicsRaw.split('\n').filter(t => t.trim());
    setLoading(btn, true);
    
    const data = {
        type: document.getElementById('bulk-type').value,
        platform: document.getElementById('bulk-platform').value,
        topics: topics
    };
    
    const result = await apiCall('/api/bulk/generate', data);
    setLoading(btn, false);
    
    if (result.status === 'ok') {
        const el = document.getElementById('bulk-result');
        el.classList.remove('hidden');
        let html = `<h3>⚡ ${result.results.length} Items Generated</h3>`;
        result.results.forEach((r, i) => {
            if (r.status === 'ok') {
                html += `<div style="border-bottom:1px solid var(--border);padding:12px 0">
                    <h4 style="color:var(--accent);margin-bottom:8px">${i+1}. ${r.topic}</h4>
                    <div style="font-size:13px">${formatContent(r.content)}</div>
                </div>`;
            }
        });
        el.innerHTML = html;
    }
}

// ============ TEMPLATES ============
async function saveTemplate() {
    const name = document.getElementById('tpl-name').value;
    const content = document.getElementById('tpl-content').value;
    if (!name || !content) return alert('Isi nama dan content');
    
    await apiCall('/api/templates', {
        name: name,
        category: document.getElementById('tpl-category').value,
        content: content
    });
    
    document.getElementById('tpl-name').value = '';
    document.getElementById('tpl-content').value = '';
    loadTemplates();
}

async function loadTemplates() {
    const resp = await fetch('/api/templates');
    const data = await resp.json();
    const el = document.getElementById('templates-list');
    
    if (!data.templates || data.templates.length === 0) {
        el.innerHTML = '<p style="color:var(--text-muted)">Belum ada template</p>';
        return;
    }
    
    el.innerHTML = data.templates.map(t => `
        <div class="schedule-item">
            <div class="info">
                <h4>${t.name}</h4>
                <span style="font-size:12px;color:var(--text-muted)">${t.category} • ${(t.content || '').substring(0, 80)}...</span>
            </div>
            <div>
                <button class="copy-btn" onclick="navigator.clipboard.writeText(\`${t.content.replace(/`/g, '\\`').replace(/\\/g, '\\\\')}\`);this.textContent='✅'">📋</button>
                <button class="btn-delete" onclick="deleteTemplate('${t.id}')">🗑️</button>
            </div>
        </div>
    `).join('');
}

async function deleteTemplate(id) {
    await fetch(`/api/templates/${id}`, {method: 'DELETE'});
    loadTemplates();
}

// ============ SCHEDULE ============
async function createSchedule() {
    const data = {
        title: document.getElementById('sched-title').value,
        platform: document.getElementById('sched-platform').value,
        content: document.getElementById('sched-content').value,
        scheduled_at: document.getElementById('sched-date').value
    };
    if (!data.title || !data.scheduled_at) return alert('Isi judul dan jadwal');
    
    await apiCall('/api/schedule/create', data);
    document.getElementById('sched-title').value = '';
    document.getElementById('sched-content').value = '';
    loadSchedules();
}

async function loadSchedules() {
    const resp = await fetch('/api/schedule/list');
    const data = await resp.json();
    const el = document.getElementById('schedule-list');
    
    if (!data.schedules || data.schedules.length === 0) {
        el.innerHTML = '<p style="color:var(--text-muted)">Belum ada jadwal</p>';
        return;
    }
    
    el.innerHTML = data.schedules.map(s => `
        <div class="schedule-item">
            <div class="info">
                <h4>${s.title}</h4>
                <span>${s.scheduled_at} • ${s.content || ''}</span>
            </div>
            <div>
                <span class="badge">${s.platform}</span>
                <button class="btn-delete" onclick="deleteSchedule(${s.id})">🗑️</button>
            </div>
        </div>
    `).join('');
}

async function deleteSchedule(id) {
    await fetch(`/api/schedule/${id}`, {method: 'DELETE'});
    loadSchedules();
}

async function exportCSV() {
    const resp = await fetch('/api/export/csv', {method: 'POST'});
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'content_calendar.csv';
    a.click();
}

// ============ HISTORY ============
async function loadHistory(type) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
    
    const resp = await fetch(`/api/history/${type}`);
    const data = await resp.json();
    const el = document.getElementById('history-list');
    const items = data[type] || [];
    
    if (items.length === 0) {
        el.innerHTML = '<p style="color:var(--text-muted)">Belum ada history</p>';
        return;
    }
    
    el.innerHTML = items.map(item => `
        <div class="schedule-item">
            <div class="info">
                <h4>${item.title || item.platform || 'Untitled'}</h4>
                <span>${(item.content || '').substring(0, 100)}...</span>
            </div>
            <span class="badge">${item.created_at}</span>
        </div>
    `).join('');
}

// Init
loadSchedules();
