import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import (
    DATA_DIR,
    RESUMES_DIR,
    COVER_LETTERS_DIR,
    MASTER_PROFILE_PATH,
    DEFAULT_PROVIDER,
    DEFAULT_GEMINI_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_ANTHROPIC_MODEL,
    DEFAULT_OLLAMA_MODEL,
    DEFAULT_OLLAMA_URL,
)
from core.parser import extract_document_text
from core.llm_client import LLMClient
from core.prompt_engine import (
    MASTER_PROFILE_SYSTEM_PROMPT,
    get_extract_master_profile_prompt,
    TAILORING_SYSTEM_PROMPT,
    get_tailor_resume_prompt,
    parse_tailoring_response,
    COVER_LETTER_SYSTEM_PROMPT,
    get_cover_letter_prompt,
)
from core.templates import DEFAULT_MASTER_PROFILE, markdown_to_styled_html
from core.pdf_generator import generate_pdf_from_markdown

app = FastAPI(title="AI Resume Maker & ATS Tailor", version="1.0.0")

# Mount static directory
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Request Models
class LLMTestRequest(BaseModel):
    provider: str
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None

class ProfileUpdateRequest(BaseModel):
    content: str

class TailorResumeRequest(BaseModel):
    job_description: str
    target_role: Optional[str] = ""
    target_company: Optional[str] = ""
    tone: Optional[str] = "Action-Oriented & Metrics-Driven"
    length_style: Optional[str] = "1 Page Strict (ATS Standard)"
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    theme: Optional[str] = "modern"
    paper_size: Optional[str] = "A4"

class SaveResumeRequest(BaseModel):
    filename: Optional[str] = None
    content: str
    target_role: Optional[str] = "Custom"

class CoverLetterRequest(BaseModel):
    job_description: str
    target_role: Optional[str] = ""
    target_company: Optional[str] = ""
    tone: Optional[str] = "Action-Oriented & Metrics-Driven"
    provider: Optional[str] = None
    api_key: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None

class RenderHtmlRequest(BaseModel):
    markdown: str
    theme: Optional[str] = "modern"
    paper_size: Optional[str] = "A4"

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if not index_file.exists():
        raise HTTPException(status_code=404, detail="index.html not found")
    with open(index_file, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.get("/api/config")
async def get_system_config():
    """Return default configuration and environment hints."""
    has_gemini = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    
    return {
        "default_provider": DEFAULT_PROVIDER,
        "models": {
            "gemini": DEFAULT_GEMINI_MODEL,
            "openai": DEFAULT_OPENAI_MODEL,
            "anthropic": DEFAULT_ANTHROPIC_MODEL,
            "ollama": DEFAULT_OLLAMA_MODEL,
        },
        "ollama_url": DEFAULT_OLLAMA_URL,
        "detected_keys": {
            "gemini": has_gemini,
            "openai": has_openai,
            "anthropic": has_anthropic,
        }
    }

@app.get("/api/profile")
async def get_master_profile():
    """Retrieve or initialize the candidate's master profile."""
    if not MASTER_PROFILE_PATH.exists():
        with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MASTER_PROFILE.strip())
            
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content, "exists": True}

@app.post("/api/profile")
async def save_master_profile(req: ProfileUpdateRequest):
    """Save updated master profile markdown."""
    with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
        f.write(req.content)
    return {"success": True, "message": "Master profile saved successfully."}

@app.post("/api/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    format_with_ai: bool = Form(True),
    provider: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    model: Optional[str] = Form(None),
    base_url: Optional[str] = Form(None),
):
    """
    Extracts text from uploaded PDF/Word resume, formats it into a structured
    Master Profile via LLM, and persists it.
    """
    try:
        content_bytes = await file.read()
        raw_text = extract_document_text(file.filename or "resume.pdf", content_bytes)
        
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract any text from uploaded file.")

        final_profile_md = raw_text
        ai_formatted = False

        if format_with_ai:
            try:
                llm = LLMClient(
                    provider=provider or DEFAULT_PROVIDER,
                    api_key=api_key,
                    model=model,
                    base_url=base_url
                )
                prompt = get_extract_master_profile_prompt(raw_text)
                ai_result = await llm.generate(prompt, system_prompt=MASTER_PROFILE_SYSTEM_PROMPT)
                if ai_result and ("#" in ai_result or "##" in ai_result):
                    final_profile_md = ai_result.strip()
                    ai_formatted = True
            except Exception as e:
                # If LLM formatting fails, fallback to raw extracted text with a note
                final_profile_md = f"# Extracted Resume\n\n> Note: AI structuring failed ({str(e)}). Showing raw extracted text:\n\n{raw_text}"

        with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
            f.write(final_profile_md)

        return {
            "success": True,
            "filename": file.filename,
            "ai_formatted": ai_formatted,
            "content": final_profile_md,
            "raw_length": len(raw_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process uploaded file: {str(e)}")

@app.post("/api/test-llm")
async def test_llm_connection(req: LLMTestRequest):
    """Verify credentials and connectivity for an LLM provider."""
    client = LLMClient(
        provider=req.provider,
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url
    )
    result = await client.test_connection()
    return result

@app.post("/api/tailor")
async def tailor_resume(req: TailorResumeRequest):
    """
    Tailor candidate's resume to match a specific Job Description.
    Saves the output to data/resumes/ and returns markdown + ATS analysis.
    """
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    # Load master profile
    if not MASTER_PROFILE_PATH.exists():
        with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MASTER_PROFILE.strip())
            
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        master_profile_md = f.read()

    llm = LLMClient(
        provider=req.provider or DEFAULT_PROVIDER,
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url
    )

    prompt = get_tailor_resume_prompt(
        master_profile_md=master_profile_md,
        job_description=req.job_description,
        target_role=req.target_role or "",
        target_company=req.target_company or "",
        tone=req.tone or "Action-Oriented & Metrics-Driven",
        length_style=req.length_style or "1-2 Pages Balanced"
    )

    try:
        raw_response = await llm.generate(prompt, system_prompt=TAILORING_SYSTEM_PROMPT)
        resume_md, ats_analysis = parse_tailoring_response(raw_response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating tailored resume: {str(e)}")

    # Create timestamped filename
    role_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', req.target_role or "Tailored_Resume").strip("_")
    company_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', req.target_company or "").strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    parts = [p for p in [role_slug, company_slug, timestamp] if p]
    base_filename = "_".join(parts)
    
    md_filename = f"{base_filename}.md"
    pdf_filename = f"{base_filename}.pdf"
    
    md_path = RESUMES_DIR / md_filename
    pdf_path = RESUMES_DIR / pdf_filename

    # Save Markdown file
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(resume_md)

    # Generate standalone PDF and HTML
    pdf_success, pdf_msg = generate_pdf_from_markdown(
        resume_md,
        pdf_path,
        theme=req.theme or "modern",
        paper_size=req.paper_size or "A4"
    )

    return {
        "success": True,
        "filename": md_filename,
        "pdf_filename": pdf_filename,
        "resume_markdown": resume_md,
        "ats_analysis": ats_analysis,
        "pdf_available": pdf_success,
        "pdf_status": pdf_msg,
        "saved_at": timestamp
    }

@app.get("/api/resumes")
async def list_resumes():
    """List all saved tailored resumes in data/resumes/."""
    items = []
    if RESUMES_DIR.exists():
        for p in sorted(RESUMES_DIR.glob("*.md"), key=lambda f: f.stat().st_mtime, reverse=True):
            pdf_sibling = p.with_suffix(".pdf")
            items.append({
                "filename": p.name,
                "pdf_filename": pdf_sibling.name if pdf_sibling.exists() else None,
                "created_at": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "size_bytes": p.stat().st_size
            })
    return {"resumes": items}

@app.get("/api/resumes/{filename}")
async def get_resume_by_name(filename: str):
    """Retrieve the markdown content of a specific resume."""
    file_path = RESUMES_DIR / filename
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Resume file not found.")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return {"filename": filename, "content": content}

@app.post("/api/save-resume")
async def save_edited_resume(req: SaveResumeRequest):
    """Save an edited markdown resume file."""
    if req.filename:
        target_path = RESUMES_DIR / req.filename
    else:
        role_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', req.target_role or "Resume").strip("_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_path = RESUMES_DIR / f"{role_slug}_{timestamp}.md"

    with open(target_path, "w", encoding="utf-8") as f:
        f.write(req.content)

    # Update PDF companion as well
    pdf_path = target_path.with_suffix(".pdf")
    generate_pdf_from_markdown(req.content, pdf_path)

    return {"success": True, "filename": target_path.name}

@app.post("/api/render-html", response_class=HTMLResponse)
async def render_html_preview(req: RenderHtmlRequest):
    """Render markdown into standalone styled HTML for live preview or print."""
    html = markdown_to_styled_html(req.markdown, theme=req.theme or "modern", paper_size=req.paper_size or "A4")
    return HTMLResponse(content=html)

@app.post("/api/cover-letter")
async def generate_tailored_cover_letter(req: CoverLetterRequest):
    """Generate a tailored, high-impact Cover Letter from Master Profile and JD."""
    if not req.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    if not MASTER_PROFILE_PATH.exists():
        with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MASTER_PROFILE.strip())
            
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        master_profile_md = f.read()

    llm = LLMClient(
        provider=req.provider or DEFAULT_PROVIDER,
        api_key=req.api_key,
        model=req.model,
        base_url=req.base_url
    )

    prompt = get_cover_letter_prompt(
        master_profile_md=master_profile_md,
        job_description=req.job_description,
        target_role=req.target_role or "",
        target_company=req.target_company or "",
        tone=req.tone or "Action-Oriented & Metrics-Driven"
    )

    try:
        raw_response = await llm.generate(prompt, system_prompt=COVER_LETTER_SYSTEM_PROMPT)
        cover_letter_md = raw_response.strip()
        # Clean any accidental outer markdown code fences
        if cover_letter_md.startswith("```markdown"):
            cover_letter_md = cover_letter_md[11:]
        elif cover_letter_md.startswith("```"):
            cover_letter_md = cover_letter_md[3:]
        if cover_letter_md.endswith("```"):
            cover_letter_md = cover_letter_md[:-3]
        cover_letter_md = cover_letter_md.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating cover letter: {str(e)}")

    role_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', req.target_role or "Role").strip("_")
    company_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', req.target_company or "Company").strip("_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"Cover_Letter_{role_slug}_{company_slug}_{timestamp}.md"
    file_path = COVER_LETTERS_DIR / filename

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(cover_letter_md)

    return {
        "success": True,
        "filename": filename,
        "cover_letter_markdown": cover_letter_md,
        "saved_at": timestamp
    }

@app.get("/api/download-letter/{filename}")
async def download_cover_letter(filename: str):
    file_path = COVER_LETTERS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Cover letter file not found")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="text/markdown"
    )

@app.get("/api/download-md/{filename}")
async def download_markdown(filename: str):
    file_path = RESUMES_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="text/markdown"
    )

@app.get("/api/download-pdf/{filename}")
async def download_pdf(filename: str):
    pdf_path = RESUMES_DIR / filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found. Please use the Print to PDF button in preview.")
    return FileResponse(
        path=str(pdf_path),
        filename=filename,
        media_type="application/pdf"
    )

