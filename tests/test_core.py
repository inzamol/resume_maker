import unittest
from core.prompt_engine import (
    get_tailor_resume_prompt,
    get_cover_letter_prompt,
    get_extract_master_profile_prompt,
    parse_tailoring_response,
)
from core.templates import markdown_to_styled_html
from core.parser import clean_extracted_text

class TestCoreModules(unittest.TestCase):
    def test_resume_prompt_contains_1page_constraint(self):
        prompt = get_tailor_resume_prompt(
            master_profile_md="# John Doe\nSoftware Engineer",
            job_description="Looking for Python Engineer",
            target_role="Python Engineer",
            target_company="Acme Corp",
            tone="Professional",
            length_style="1 Page Strict (ATS Standard)"
        )
        self.assertIn("MANDATORY: MUST FIT ON EXACTLY 1 PAGE", prompt)
        self.assertIn("Acme Corp", prompt)
        self.assertIn("Python Engineer", prompt)

    def test_cover_letter_prompt(self):
        prompt = get_cover_letter_prompt(
            master_profile_md="# John Doe\nSoftware Engineer",
            job_description="Looking for Python Engineer",
            target_role="Python Engineer",
            target_company="Acme Corp"
        )
        self.assertIn("Acme Corp", prompt)
        self.assertIn("Target Role: Python Engineer", prompt)

    def test_compile_resume_html(self):
        md = "# John Doe\n\n## Experience\n\n### Lead Engineer | Acme Corp\n- Built scalable APIs"
        html = markdown_to_styled_html(md, theme="modern", paper_size="A4")
        self.assertIn("theme-modern", html)
        self.assertIn("John Doe", html)
        self.assertIn("Acme Corp", html)

    def test_clean_extracted_text(self):
        dirty = "  John Doe  \n\n\n\n\n  Software Engineer  \n   "
        cleaned = clean_extracted_text(dirty)
        self.assertEqual(cleaned, "John Doe\n\nSoftware Engineer")

    def test_parse_tailoring_response_json(self):
        mock_response = '''```json
{
  "resume_markdown": "# John Doe\\n\\nSoftware Engineer",
  "ats_analysis": {
    "match_score": 92,
    "matched_keywords": ["Python", "FastAPI"],
    "missing_keywords": ["Docker"],
    "tailoring_summary": "Tailored for senior backend position.",
    "interview_tips": ["Mention scaling Kafka."]
  }
}
```'''
        md, ats = parse_tailoring_response(mock_response)
        self.assertEqual(md, "# John Doe\n\nSoftware Engineer")
        self.assertEqual(ats["match_score"], 92)
        self.assertEqual(len(ats["matched_keywords"]), 2)

if __name__ == '__main__':
    unittest.main()
