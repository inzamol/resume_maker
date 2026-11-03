import io
from pathlib import Path
from typing import Union
import pypdf
import docx

def clean_extracted_text(text: str) -> str:
    """Normalize extracted text whitespace and characters."""
    lines = [line.strip() for line in text.splitlines()]
    # Remove consecutive empty lines (more than 1 empty line between paragraphs)
    cleaned_lines = []
    empty_count = 0
    for line in lines:
        if not line:
            empty_count += 1
            if empty_count <= 1:
                cleaned_lines.append("")
        else:
            empty_count = 0
            cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def extract_text_from_pdf(source: Union[bytes, str, Path]) -> str:
    """Extract text from a PDF file or bytes using pypdf."""
    stream = io.BytesIO(source) if isinstance(source, bytes) else open(source, "rb")
    try:
        reader = pypdf.PdfReader(stream)
        text_chunks = []
        for i, page in enumerate(reader.pages):
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text)
        return clean_extracted_text("\n\n".join(text_chunks))
    finally:
        if not isinstance(source, bytes):
            stream.close()

def extract_text_from_docx(source: Union[bytes, str, Path]) -> str:
    """Extract text from a DOCX file or bytes using python-docx."""
    stream = io.BytesIO(source) if isinstance(source, bytes) else source
    doc = docx.Document(stream)
    chunks = []
    
    # Paragraphs
    for p in doc.paragraphs:
        if p.text.strip():
            chunks.append(p.text.strip())
            
    # Tables (often used in resumes for skills/dates)
    for table in doc.tables:
        for row in table.rows:
            row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if row_cells:
                # Remove duplicates in adjacent merged cells
                deduped = []
                for cell in row_cells:
                    if not deduped or cell != deduped[-1]:
                        deduped.append(cell)
                chunks.append(" | ".join(deduped))
                
    return clean_extracted_text("\n".join(chunks))

def extract_document_text(filename: str, content: bytes) -> str:
    """Detect file type and extract clean text."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(content)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(content)
    elif ext in [".txt", ".md", ".markdown"]:
        return clean_extracted_text(content.decode("utf-8", errors="replace"))
    else:
        # Fallback to UTF-8 text attempt
        try:
            return clean_extracted_text(content.decode("utf-8"))
        except Exception:
            raise ValueError(f"Unsupported file format: {ext}. Please upload a PDF, DOCX, or Markdown file.")

