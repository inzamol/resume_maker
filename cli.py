import argparse
import asyncio
import os
import sys
from pathlib import Path

from config import MASTER_PROFILE_PATH, DEFAULT_PROVIDER, RESUMES_DIR, COVER_LETTERS_DIR
from core.llm_client import LLMClient
from core.prompt_engine import (
    TAILORING_SYSTEM_PROMPT,
    get_tailor_resume_prompt,
    parse_tailoring_response,
    COVER_LETTER_SYSTEM_PROMPT,
    get_cover_letter_prompt,
)
from core.templates import DEFAULT_MASTER_PROFILE
from core.pdf_generator import generate_pdf_from_markdown

async def main():
    parser = argparse.ArgumentParser(description="Tailor resume from a Job Description and export Markdown & PDF.")
    parser.add_argument("--jd", type=str, required=True, help="Job description text or path to a text file containing the JD.")
    parser.add_argument("--role", type=str, default="", help="Target job title.")
    parser.add_argument("--company", type=str, default="", help="Target company name.")
    parser.add_argument("--provider", type=str, default=DEFAULT_PROVIDER, help="AI provider (gemini, openai, anthropic, ollama).")
    parser.add_argument("--api-key", type=str, default=None, help="LLM API key (or use env var).")
    parser.add_argument("--model", type=str, default=None, help="Model name.")
    parser.add_argument("--theme", type=str, default="modern", choices=["modern", "classic", "tech"], help="Resume CSS theme.")
    parser.add_argument("--paper", type=str, default="A4", choices=["A4", "Letter"], help="Paper size.")
    parser.add_argument("--out", type=str, default=None, help="Output markdown path (e.g. output.md).")
    parser.add_argument("--pdf", action="store_true", help="Generate companion PDF file.")
    parser.add_argument("--cover-letter", action="store_true", help="Also generate a matching tailored Cover Letter.")

    args = parser.parse_args()

    # Read JD
    jd_content = args.jd
    if os.path.exists(args.jd):
        with open(args.jd, "r", encoding="utf-8") as f:
            jd_content = f.read()

    if not jd_content.strip():
        print("Error: Job description is empty.")
        sys.exit(1)

    # Read Master Profile
    if not MASTER_PROFILE_PATH.exists():
        with open(MASTER_PROFILE_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_MASTER_PROFILE)
    with open(MASTER_PROFILE_PATH, "r", encoding="utf-8") as f:
        master_profile_md = f.read()

    print(f"[*] Tailoring resume using {args.provider}...")
    llm = LLMClient(provider=args.provider, api_key=args.api_key, model=args.model)
    prompt = get_tailor_resume_prompt(
        master_profile_md=master_profile_md,
        job_description=jd_content,
        target_role=args.role,
        target_company=args.company
    )

    try:
        raw = await llm.generate(prompt, system_prompt=TAILORING_SYSTEM_PROMPT)
        resume_md, ats = parse_tailoring_response(raw)
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

    out_path = Path(args.out) if args.out else (RESUMES_DIR / f"{args.role or 'Tailored'}_resume.md")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(resume_md)

    print(f"[✓] Tailored resume saved: {out_path}")
    if ats.get("match_score"):
        print(f"[*] ATS Fit Score: {ats['match_score']}%")
    if ats.get("matched_keywords"):
        print(f"[*] Matched Keywords: {', '.join(ats['matched_keywords'][:8])}")

    if args.cover_letter:
        print("[*] Generating matching tailored Cover Letter...")
        letter_prompt = get_cover_letter_prompt(
            master_profile_md=master_profile_md,
            job_description=jd_content,
            target_role=args.role,
            target_company=args.company
        )
        try:
            letter_md = await llm.generate(letter_prompt, system_prompt=COVER_LETTER_SYSTEM_PROMPT)
            letter_path = out_path.with_name(f"{out_path.stem}_Cover_Letter.md")
            with open(letter_path, "w", encoding="utf-8") as f:
                f.write(letter_md.strip())
            print(f"[✓] Cover letter saved: {letter_path}")
        except Exception as e:
            print(f"[!] Cover letter generation error: {e}")

    if args.pdf:
        pdf_path = out_path.with_suffix(".pdf")
        ok, msg = generate_pdf_from_markdown(resume_md, pdf_path, theme=args.theme, paper_size=args.paper)
        if ok:
            print(f"[✓] PDF created: {pdf_path}")
        else:
            print(f"[!] PDF note: {msg}")

if __name__ == "__main__":
    asyncio.run(main())

