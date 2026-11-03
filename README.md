# ⚡ AI Resume Architect & ATS Tailor

A powerful, customizable system that transforms your master career history into an ATS-optimized, beautifully styled Markdown resume tailored specifically to any Job Description (JD), with 1-click export to PDF.

---

## ✨ Features

- **Split-Screen Web Interface**:
  - **Left**: Paste Job Description, select tone & length, upload/edit Master Profile, configure AI providers, or browse resume history.
  - **Right**: Live rendered ATS-friendly PDF Preview, in-place Markdown code editor, and interactive ATS match analysis.
- **Upload Existing Resume**:
  - Supports **PDF**, **Word (.docx)**, and **Markdown (.md)**.
  - Automatically extracts and formats your career background into a persistent **Master Profile** (`data/master_profile.md`).
- **Configurable Multi-Provider AI**:
  - **Google Gemini** (Gemini 2.5 Flash / 1.5 Flash - fast & free tier supported)
  - **OpenAI** (GPT-4o, GPT-4o-mini)
  - **Anthropic Claude** (Claude 3.5 Sonnet / Haiku)
  - **Ollama** (Local LLM - 100% private, free, and offline)
  - **Custom OpenAI-compatible** endpoints (Groq, OpenRouter, Together AI)
- **Real-Time ATS Keyword & Gap Analysis**:
  - Instant ATS Fit Score (0–100%)
  - Matched keywords pill list
  - Missing skills / gap highlights to help you prepare for technical interviews
- **Dual Rich Resume Editor**:
  - **Direct On-Paper WYSIWYG Editing**: Click **"Edit Directly on Paper"** to type, fix, bold, and reword bullet points right on the rendered paper sheet. Edits automatically sync back to clean Markdown in real-time via Turndown.js.
  - **Rich Markdown Studio Toolbar**: Format headers (H1/H2/H3), bold, italics, bullet lists, numbered lists, links, insert Google XYZ formula bullets (`+ XYZ Bullet`), add job role or project blocks, and insert action verbs with 1 click.
  - **Live Editor Stats**: Tracks character count, word count, and lines in real-time.
- **1-Page Guarantee & ATS Formatting**:
  - Automatically structures experiences, summaries, and bullet points to fit strictly on **1 single page** (~350–450 words) adhering to modern tech industry standards.
  - Interactive **1-Page Live Fit Badge** (`✓ 1 Page Fit` or overflow alert) and visual page boundary guide in the preview canvas.
- **1-Click Tailored Cover Letter Generator**:
  - Automatically drafts a compelling, personalized cover letter matching the target JD and company.
  - Dedicated business letterhead preview with 1-click clipboard copy, `.md` download, and Print-to-PDF.
- **Print & PDF Export**:
  - **1-Click Direct Vector PDF Export** via `html2pdf.js`
  - **Pixel-Perfect Print-to-PDF** via browser print engine (`@media print` formatted for A4 & US Letter)
  - **3 Professional Resume Themes**: Modern Clean (Sans), Classic Executive (Serif), and Minimalist Tech (Mono)
  - Automatic page-break management (`page-break-inside: avoid` on job roles and project blocks)
- **CLI Support**:
  - Run from the command line for fast scripting and batch tailoring: `python cli.py --jd job.txt --pdf`

---

## 🚀 Quick Start

### 1. Launch the Web Application (Recommended)

On Windows, simply double-click **`run.bat`** or run:

```powershell
.\run.bat
```

Or manually via terminal:

```powershell
# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

# Start the server
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at **[http://localhost:8000](http://localhost:8000)**.

---

## 🛠️ How to Use

1. **Set Up Your Master Profile**:
   - Navigate to the **Master Profile** tab in the left pane.
   - Click **Browse File** or drag & drop your existing resume (PDF or DOCX).
   - The system extracts your experience into `data/master_profile.md`. You can fine-tune or add new achievements anytime.
2. **Configure Your AI Engine**:
   - Go to the **AI Engine** tab.
   - Choose your provider (e.g., Google Gemini).
   - Enter your API Key (e.g. from [Google AI Studio](https://aistudio.google.com/)) or set `GEMINI_API_KEY` in `.env`.
   - Click **Test Connection** to verify.
3. **Paste Job Description & Tailor**:
   - Go to the **Job Spec** tab.
   - Paste the job posting into the text area.
   - (Optional) Enter the Target Role Name and Company.
   - Click **Tailor Resume for this Job**.
4. **Review, Edit & Export**:
   - Preview the formatted resume in real-time.
   - Switch themes (Modern, Classic, Tech) or paper sizes (A4 / Letter).
   - Inspect the **ATS Match Score** tab for keyword match statistics.
   - Click **Export PDF** or **Print** to save your ready-to-send resume.

---

## 💻 CLI Usage

You can also run the system headlessly from the terminal:

```powershell
.\.venv\Scripts\python.exe cli.py --jd "job_description.txt" --role "Staff Backend Engineer" --company "Stripe" --pdf --cover-letter
```

### CLI Arguments:
- `--jd`: Path to text file or raw job description string.
- `--role`: Target job title.
- `--company`: Target company name.
- `--provider`: `gemini` (default), `openai`, `anthropic`, or `ollama`.
- `--theme`: `modern`, `classic`, or `tech`.
- `--paper`: `A4` or `Letter`.
- `--pdf`: Flag to automatically generate a companion PDF file.
- `--cover-letter`: Flag to generate a matching tailored Cover Letter (`.md`).

---

## 📂 Project Structure

```text
resume_maker/
├── app.py                      # FastAPI server & REST API
├── cli.py                      # Command-line interface
├── config.py                   # App configuration & paths
├── run.bat                     # 1-click Windows launcher
├── requirements.txt            # Python dependencies
├── core/
│   ├── parser.py               # PDF/Word/Markdown text extractor
│   ├── llm_client.py           # Multi-provider LLM connector
│   ├── prompt_engine.py        # Tailoring & ATS optimization logic
│   ├── pdf_generator.py        # PDF & HTML generation engine
│   └── templates.py            # Themes, CSS, and default profiles
├── static/
│   ├── index.html              # Modern Split-screen Web UI
│   ├── css/
│   │   └── resume_themes.css   # Print-ready CSS for A4/Letter
│   └── js/
│       └── app.js              # Live Markdown rendering & sync
└── data/
    ├── master_profile.md       # Your persistent career profile
    └── resumes/                # Generated tailored resumes (.md & .pdf)
```

