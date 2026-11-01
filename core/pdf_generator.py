import os
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from core.templates import markdown_to_styled_html

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

def find_browser_executable() -> Optional[str]:
    for p in EDGE_PATHS + CHROME_PATHS:
        if os.path.exists(p):
            return p
    return None

def generate_pdf_from_markdown(
    md_content: str,
    output_pdf_path: Path,
    theme: str = "modern",
    paper_size: str = "A4"
) -> Tuple[bool, str]:
    """
    Renders markdown to styled HTML and converts it to PDF using headless Edge/Chrome if available.
    Also saves the standalone HTML file alongside the PDF.
    """
    html_content = markdown_to_styled_html(md_content, theme=theme, paper_size=paper_size)
    html_path = output_pdf_path.with_suffix(".html")
    
    # Save styled HTML file
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    browser = find_browser_executable()
    if not browser:
        return False, "Headless browser not found. HTML file created; use browser print or client-side PDF export."

    try:
        # Run headless browser print
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={output_pdf_path.resolve()}",
            str(html_path.resolve())
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        
        if output_pdf_path.exists() and output_pdf_path.stat().st_size > 0:
            return True, f"PDF successfully created at {output_pdf_path.name}"
        else:
            return False, f"Browser print exited with code {result.returncode}."
    except Exception as e:
        return False, f"PDF generation error: {str(e)}"

