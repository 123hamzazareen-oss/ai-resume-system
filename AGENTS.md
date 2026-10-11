# Project Instructions & Progress State for AI Agents

> **CRITICAL INSTRUCTION FOR ALL AI AGENTS**:
> **DO NOT START FROM SCRATCH.** 
> All frontend pages, styling, and Django backend code are already implemented and active in this repository. 
> Always inspect existing files in `templates/`, `static/css/style.css`, and Django apps before making changes. Continue directly from where previous work left off.

---

## 1. Project Overview
- **Repository**: ResumeAI / AI Resume System
- **Stack**: Django (Python) + SQLite + TF-IDF Cosine Similarity (Scikit-Learn) + Google OAuth 2.0 (Gmail API) + Vanilla HTML/CSS/JS.
- **Port / Dev Server**: `http://127.0.0.1:8000/`

---

## 2. Design System & Style Guidelines (STRICT)
- **Typography Pairing**:
  - `font-display`: `'Sora', sans-serif` (Headings, page titles, brand)
  - `font-heading`: `'Outfit', sans-serif` (Section labels, card titles)
  - `font-num`: `'Space Grotesk', sans-serif` (Metrics, percentages, stats)
  - `font-code`: `'JetBrains Mono', monospace` (Timestamps, code keywords)
  - `font-body`: `'Plus Jakarta Sans', sans-serif` (Body paragraphs)
- **Icons**:
  - **NEVER USE RAW EMOJIS OR INFORMAL SIGNS** (no `✦`, `📤`, `📊`, `🎯`, `💡`, `⚠️`, `✓`).
  - Always use crisp, modern inline **SVG vector icons** (stroke-width: 2 to 2.5).
- **Navbar Rule**:
  - Navigation links must maintain `white-space: nowrap;` so items like "Upload Resume", "ATS Report", and "Job Matches" never wrap onto two lines.
- **Color Palettes**:
  - Emerald Aurora (`#10b981`, `#059669`) for high scores and active statuses.
  - Electric Indigo (`#6366f1`, `#4f46e5`) for career domain tracks.
  - Cyber Cyan (`#06b6d4`, `#0284c7`) for technical competencies.
  - Sunset Coral/Rose (`#f43f5e`, `#e11d48`) for gaps and low scores.
  - Solar Amber (`#f59e0b`, `#d97706`) for medium matches and alerts.

---

## 3. Completed Features & Current State
1. **Landing Page**:
   - Django: `templates/users/home.html` (Full modern SaaS landing page, simulator, SVG icons).
   - Standalone HTML: `frontend/index.html` (Synced standalone zero-dependency version).
2. **Global Navigation & Base**:
   - `templates/base.html`: Modern navbar, inline SVGs, Google Fonts stack, avatar pill.
3. **Dashboard (`/dashboard/`) - COMPLETED & WORKING WELL**:
   - `templates/users/dashboard.html` & `static/css/style.css`:
     - Midnight Aurora Executive Hero with frosted glass chips & pulse indicator.
     - 4 Multi-color themed KPI cards (ATS Compatibility, Career Domain, Competencies, Gaps).
     - Target Job Description Comparator (Option A library vs Option B custom paste).
     - Categorized Skill Matrix chips (Frontend, Backend, Database, AI/ML, Cloud).
     - Priority-badged AI Optimization Guidance cards.
     - Document History table with PDF/DOC badges and clean date formatting.
     - Synced Gmail Opportunities / OAuth banner.
     - Cumulative match history records table.
4. **ATS Analysis Report (`/resume/result/`)**:
   - `templates/resume_analyzer/result.html`: Matching deluxe multi-font and SVG layout.
5. **Job Matches (`/jobs/`)**:
   - `templates/job_matcher/matches.html`: Tier filter tabs, search filter, and color-coded match cards.

---

## 4. How Any Agent Must Resume Work
1. When asked to make a change, check the existing file first using `view_file`.
2. Do not overwrite or regenerate files from scratch. Use `replace_file_content` for targeted updates.
3. Preserve all Django template tags and context variables (`ats_score`, `domain_display`, `skills`, `missing_skills`, `suggestions`, `jobs`, `gmail_connected`, `previous_matches`, `recent_resumes`, `active_resume`, `available_jobs`, `custom_match_result`).
