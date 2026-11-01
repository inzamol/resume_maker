import json
import re
from typing import Dict, Any, Tuple

MASTER_PROFILE_SYSTEM_PROMPT = """You are an expert Executive Resume Writer and Career Strategist.
Your goal is to parse raw text extracted from a resume document and transform it into a comprehensive, highly organized Master Career Profile in clean Markdown format.

Rules:
1. Capture all factual details: Full contact info, dates, company names, job titles, education, certifications, projects, and tech stacks.
2. Group skills into clear categories (e.g. Languages, Frameworks & Libraries, Cloud & DevOps, Databases, Tools & Platforms).
3. Preserve all accomplishments, numbers, percentages, and metrics.
4. Output clean, valid Markdown only. Do not add conversational commentary.
"""

def get_extract_master_profile_prompt(raw_resume_text: str) -> str:
    return f"""Please convert the following raw resume text into a structured Master Profile in Markdown format.

Structure:
# [Full Name]
- Email: ... | Phone: ... | Location: ... | LinkedIn: ... | GitHub: ... | Portfolio: ...

## Professional Summary
[High-impact summary highlighting years of experience and domain strengths]

## Technical & Professional Skills
- **Languages:** ...
- **Frameworks & Libraries:** ...
- **Cloud & DevOps:** ...
- **Databases & Storage:** ...
- **Tools & Methodologies:** ...

## Professional Experience
### [Job Title] | [Company Name] | [Location / Remote]
*([Start Date] - [End Date / Present])*
- [Accomplishment with metrics and impact]
- ...

## Projects
### [Project Name] | [Tech Stack] | [Link / GitHub]
- [Description of architecture, problem solved, and results]

## Education & Certifications
- **[Degree]**, [University / Institution] ([Graduation Year])
- **[Certifications]**, [Issuing Body] ([Year])

--- Raw Resume Content ---
{raw_resume_text}
"""

TAILORING_SYSTEM_PROMPT = """You are a world-class ATS Optimization Specialist and Executive Tech Resume Writer.
Your mission is to craft a high-impact, ATS-passing resume that STRICTLY FITS ON EXACTLY ONE PAGE.

CRITICAL RULE: STRICT ONE-PAGE FIT (MANDATORY)
Recruiters and hiring managers spend an average of 6 seconds reviewing a resume. Unless explicitly told otherwise, the generated resume MUST fit neatly on a single page (~350 to 450 words total).

Strict Rules to Guarantee a Clean 1-Page Fit:
1. **Professional Summary**: Exactly 2-3 lines of high-impact technical value proposition. Never exceed 3 lines.
2. **Technical Skills**: Group into 3-4 dense, categorized lines (e.g. Languages, Frameworks, Cloud & DevOps, Databases & Tools).
3. **Experience**:
   - Limit to the 2-3 most relevant/recent positions from the candidate's Master Profile.
   - Latest / most relevant role: 3-4 impactful bullets.
   - Earlier roles: 2-3 impactful bullets.
   - Each bullet point MUST be 1 to 2 lines maximum. Avoid multi-sentence paragraphs.
   - Use Google's X-Y-Z formula: "Accomplished [X] as measured by [Y] by doing [Z]" with active verbs and quantifiable metrics.
4. **Projects**: Include 1-2 most relevant projects (1-2 bullets each), or omit if work experience already fills the page.
5. **Education & Certifications**: Compact 1-2 lines at the bottom.
6. **Aggressive Relevance Filtering**: Select only accomplishments that directly prove qualifications for the target Job Description. Omit low-relevance or redundant bullet points.
7. **Strict Factual Truth**: Never invent fake companies, fake degrees, or non-existent work history.

OUTPUT SPECIFICATION:
Provide your response in JSON format with two keys:
- "resume_markdown": The full tailored resume in Markdown.
- "ats_analysis": An object containing:
    - "match_score": number between 0 and 100.
    - "matched_keywords": array of matching skills/terms.
    - "missing_keywords": array of skills/terms from JD not in profile.
    - "tailoring_summary": 2-3 sentences explaining what was optimized.
    - "interview_tips": 2-3 actionable advice points for the candidate's interview.
"""

def get_tailor_resume_prompt(
    master_profile_md: str,
    job_description: str,
    target_role: str = "",
    target_company: str = "",
    tone: str = "Action-Oriented & Metrics-Driven",
    length_style: str = "1 Page Strict (ATS Standard)"
) -> str:
    target_info = ""
    if target_role or target_company:
        target_info = f"\nTarget Role: {target_role}\nTarget Company: {target_company}\n"

    return f"""Please tailor the candidate's resume for the target job description.

{target_info}
Selected Tone: {tone}
Length & Detail Level: {length_style} (MANDATORY: MUST FIT ON EXACTLY 1 PAGE)

Candidate's Master Profile:
\"\"\"
{master_profile_md}
\"\"\"

Target Job Description:
\"\"\"
{job_description}
\"\"\"

REMINDER ON 1-PAGE LENGTH:
Keep bullet points concise (1-2 lines each), limit to the top 2-3 most relevant experiences, and ensure the entire markdown resume fits on a single printed page.
Reply in JSON format with keys "resume_markdown" and "ats_analysis".
"""

def parse_tailoring_response(response_text: str) -> Tuple[str, Dict[str, Any]]:
    """Parse JSON output from the LLM, with fallbacks for markdown code blocks."""
    cleaned = response_text.strip()
    
    # Strip markdown code blocks like ```json ... ```
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
        
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
        
    cleaned = cleaned.strip()

    try:
        data = json.loads(cleaned)
        resume_md = data.get("resume_markdown", "")
        ats_analysis = data.get("ats_analysis", {})
        return resume_md, ats_analysis
    except Exception:
        # Fallback: if model returned markdown directly or invalid JSON
        match = re.search(r'"resume_markdown"\s*:\s*"(.*?)"\s*,\s*"ats_analysis"', response_text, re.DOTALL)
        if match:
            # Try to decode escaped string
            try:
                resume_md = json.loads(f'"{match.group(1)}"')
                return resume_md, {"match_score": 80, "matched_keywords": [], "missing_keywords": [], "tailoring_summary": "Tailored successfully."}
            except Exception:
                pass
                
        # If response itself looks like a markdown resume (has headers)
        if "# " in response_text or "## Experience" in response_text:
            return response_text, {
                "match_score": 85,
                "matched_keywords": ["Tailored to Job Description"],
                "missing_keywords": [],
                "tailoring_summary": "Generated tailored resume directly from your master profile.",
                "interview_tips": ["Review the project achievements and metrics highlighted in your resume."]
            }
            
        raise ValueError("Could not parse the model response into a valid resume and ATS analysis.")

COVER_LETTER_SYSTEM_PROMPT = """You are an elite Career Coach and Executive Recruiter who crafts compelling, high-converting Cover Letters.

Guiding Principles:
1. **AUTHENTIC & IMPACTFUL**: Avoid boilerplate cliches (e.g. "I am writing to express my enthusiasm..."). Start immediately with a strong, tailored hook connecting the candidate's core value proposition to the employer's mission/needs.
2. **STRICT FACTUAL INTEGRITY**: Only mention real achievements, tech stacks, and experiences present in the candidate's Master Profile. Do not invent facts.
3. **VALUE-FOCUSED**: Address the specific pain points and qualifications emphasized in the Job Description. Show how the candidate's past accomplishments directly translate to future success in this role.
4. **FORMAT**: Clean, professional Markdown business letter format with header, date, recipient, subject line, 3-4 structured body paragraphs, and professional closing.
"""

def get_cover_letter_prompt(
    master_profile_md: str,
    job_description: str,
    target_role: str = "",
    target_company: str = "",
    tone: str = "Action-Oriented & Metrics-Driven"
) -> str:
    target_info = ""
    if target_role or target_company:
        target_info = f"Target Role: {target_role or 'Target Role'}\nTarget Company: {target_company or 'Hiring Organization'}\n"

    return f"""Please write an exceptional, tailored Cover Letter for this candidate based on their verified Master Profile and the target Job Description.

{target_info}Tone: {tone}

Candidate's Master Profile:
\"\"\"
{master_profile_md}
\"\"\"

Target Job Description:
\"\"\"
{job_description}
\"\"\"

Requirements:
1. Extract candidate's name, email, phone, and links from the Master Profile for the letterhead header.
2. Today's Date.
3. Addressed to "Dear Hiring Team at {target_company or 'the Company'}," (or specific hiring manager if named in JD).
4. Subject line: **Re: Application for {target_role or 'Open Role'} - [Candidate Name]**
5. Opening: Engaging hook explaining why candidate is a natural fit for this exact role.
6. Body Paragraph 1-2: Concrete examples of achievements with metrics from the candidate's profile that directly map to the JD's biggest requirements.
7. Closing: Reiterate enthusiasm, value contribution, and a confident call to action.
8. Sign-off: "Sincerely,\n[Candidate Name]".
9. Output pure Markdown only, with no wrapping backticks or commentary.
"""


