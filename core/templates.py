import markdown

DEFAULT_MASTER_PROFILE = """# Alex Morgan
- **Email:** alex.morgan@email.com | **Phone:** +1 (555) 234-5678 | **Location:** San Francisco, CA
- **LinkedIn:** [linkedin.com/in/alexmorgan](https://linkedin.com) | **GitHub:** [github.com/alexmorgan](https://github.com) | **Portfolio:** [alexmorgan.dev](https://alexmorgan.dev)

## Professional Summary
Results-driven Senior Software Engineer with 6+ years of experience architecting distributed cloud systems, high-throughput microservices, and modern web applications. Proven track record of scaling platforms to 10M+ active users, reducing cloud infrastructure costs by 35%, and leading cross-functional engineering pods.

## Technical Skills
- **Languages:** Python, TypeScript, JavaScript, Go, SQL, Bash
- **Frameworks & Libraries:** FastAPI, Django, React, Next.js, Node.js, Express, Tailwind CSS
- **Cloud & DevOps:** AWS (ECS, Lambda, S3, RDS), Docker, Kubernetes, Terraform, GitHub Actions, CI/CD
- **Databases & Storage:** PostgreSQL, Redis, MongoDB, DynamoDB, Elasticsearch
- **Tools & Methodologies:** REST APIs, GraphQL, Microservices, Agile/Scrum, System Design, Unit/E2E Testing

## Professional Experience

### Senior Software Engineer | CloudScale Systems | San Francisco, CA
*(March 2022 – Present)*
- Architected and deployed an event-driven data ingestion pipeline processing 25M+ events daily using FastAPI, Kafka, and PostgreSQL, reducing latency by 42%.
- Spearheaded database query optimization and caching layer with Redis, improving p99 API response times from 450ms to 65ms.
- Mentored 5 mid-level engineers through code reviews, design docs, and automated testing standards, reducing sprint defect rate by 28%.
- Championed automated CI/CD migration to GitHub Actions, shortening release deployment cycles from 2 hours to 12 minutes.

### Software Engineer | FinTech Wave | San Jose, CA
*(July 2019 – February 2022)*
- Developed secure payment processing microservices integrating Stripe and Plaid APIs, supporting $50M+ in annual transaction volume.
- Collaborated with frontend engineers to build a real-time analytics dashboard in React/TypeScript, boosting daily active user engagement by 22%.
- Designed resilient fault-tolerant retry workflows with Celery and RabbitMQ, cutting transaction timeout failures by 99.4%.

## Key Projects

### OpenResume AI | [github.com/alexmorgan/openresume](https://github.com)
- Developed an open-source resume generator using Python and modern web standards with 1.2k+ GitHub stars.
- Implemented real-time AST markdown parsing and client-side vector PDF generation.

### Distributed Task Scheduler | Go, Redis, Docker
- Built a lightweight distributed cron engine capable of scheduling 100k tasks per minute with leader election.

## Education & Certifications
- **B.S. in Computer Science**, University of California, Berkeley (2019)
- **AWS Certified Solutions Architect – Associate** (2023)
"""

def markdown_to_styled_html(md_content: str, theme: str = "modern", paper_size: str = "A4") -> str:
    """Convert Markdown to a standalone HTML document styled for high-resolution display and printing."""
    # Convert markdown with useful extensions
    html_body = markdown.markdown(
        md_content,
        extensions=[
            "extra",
            "nl2br",
            "sane_lists",
            "tables"
        ]
    )

    theme_class = f"theme-{theme}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Preview & Print</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:wght@300;400;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        @page {{
            size: {paper_size};
            margin: 9mm 12mm;
        }}
        @media print {{
            body {{
                background: white !important;
                padding: 0 !important;
                margin: 0 !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
            .resume-sheet {{
                box-shadow: none !important;
                border: none !important;
                width: 100% !important;
                min-height: auto !important;
                padding: 0 !important;
            }}
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            background: #f1f5f9;
            color: #1e293b;
            font-size: 9.25pt;
            line-height: 1.36;
            margin: 0;
            padding: 24px;
            display: flex;
            justify-content: center;
        }}

        .resume-sheet {{
            background: white;
            width: 210mm;
            min-height: 297mm;
            padding: 10mm 14mm;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            border-radius: 4px;
            position: relative;
        }}

        /* Theme 1: Modern Clean */
        .theme-modern {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #0f172a;
        }}
        .theme-modern h1 {{
            font-size: 18pt;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin: 0 0 3px 0;
            color: #0f172a;
            text-align: center;
            line-height: 1.15;
        }}
        .theme-modern h1 + ul,
        .theme-modern h1 + p {{
            text-align: center;
            font-size: 8.5pt;
            color: #475569;
            margin-bottom: 8px;
            list-style: none;
            padding: 0;
            line-height: 1.25;
        }}
        .theme-modern h2 {{
            font-size: 9.75pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: #1e3a8a;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 1.5px;
            margin-top: 7px;
            margin-bottom: 3px;
            page-break-after: avoid;
            line-height: 1.2;
        }}
        .theme-modern h3 {{
            font-size: 9.25pt;
            font-weight: 600;
            margin-top: 4px;
            margin-bottom: 1px;
            color: #1e293b;
            display: flex;
            justify-content: space-between;
            page-break-after: avoid;
            line-height: 1.25;
        }}
        .theme-modern em, .theme-modern p > em {{
            font-size: 8pt;
            color: #64748b;
            font-style: italic;
            display: block;
            margin-bottom: 2px;
            line-height: 1.2;
        }}

        /* Theme 2: Classic Executive */
        .theme-classic {{
            font-family: 'Merriweather', Georgia, serif;
            color: #111827;
        }}
        .theme-classic h1 {{
            font-size: 17.5pt;
            font-weight: 700;
            text-align: center;
            margin-bottom: 2px;
            color: #111827;
            line-height: 1.15;
        }}
        .theme-classic h1 + ul,
        .theme-classic h1 + p {{
            text-align: center;
            font-size: 8.5pt;
            color: #374151;
            margin-bottom: 8px;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            list-style: none;
            padding: 0;
            line-height: 1.25;
        }}
        .theme-classic h2 {{
            font-size: 9.5pt;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #111827;
            border-bottom: 1px solid #111827;
            padding-bottom: 1px;
            margin-top: 7px;
            margin-bottom: 3px;
            page-break-after: avoid;
            line-height: 1.2;
        }}
        .theme-classic h3 {{
            font-size: 9.25pt;
            font-weight: 700;
            margin-top: 4px;
            margin-bottom: 1px;
            color: #111827;
            page-break-after: avoid;
            line-height: 1.25;
        }}

        /* Theme 3: Minimalist Tech */
        .theme-tech {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #18181b;
        }}
        .theme-tech h1 {{
            font-size: 17pt;
            font-weight: 700;
            letter-spacing: -0.5px;
            margin-bottom: 2px;
            line-height: 1.15;
        }}
        .theme-tech h2 {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 9.25pt;
            font-weight: 600;
            color: #0284c7;
            border-bottom: 1px dashed #cbd5e1;
            padding-bottom: 1.5px;
            margin-top: 7px;
            margin-bottom: 3px;
            line-height: 1.2;
        }}
        .theme-tech h3 {{
            font-size: 9pt;
            font-weight: 600;
            margin-top: 4px;
            margin-bottom: 1px;
            line-height: 1.25;
        }}

        /* General Typography & Elements */
        p {{
            margin: 2px 0;
            line-height: 1.35;
        }}

        ul {{
            margin: 1.5px 0 3px 0;
            padding-left: 15px;
        }}

        li {{
            margin-bottom: 2px;
            line-height: 1.34;
        }}

        a {{
            color: inherit;
            text-decoration: none;
        }}

        strong {{
            font-weight: 600;
            color: #0f172a;
        }}

        /* Page break controls */
        h2, h3 {{
            page-break-after: avoid;
            break-after: avoid;
        }}

        ul, li, p {{
            page-break-inside: auto;
        }}

        .job-block, .project-block {{
            page-break-inside: avoid;
            break-inside: avoid;
        }}
    </style>
</head>
<body>
    <div class="resume-sheet {theme_class}">
        {html_body}
    </div>
</body>
</html>"""

