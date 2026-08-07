import re

def extract_resume_sections(text):
    sections = {
        "education": "",
        "experience": "",
        "skills": "",
        "certifications": "",
        "projects": "",
        "summary": "",
    }

    patterns = {
        "education": r"(education|academics)[\s\S]{0,2000}",
        "experience": r"(experience|work history|employment)[\s\S]{0,2000}",
        "skills": r"(skills|technologies|tools)[\s\S]{0,2000}",
        "certifications": r"(certifications|certificates)[\s\S]{0,1000}",
        "projects": r"(projects|portfolio)[\s\S]{0,1500}",
        "summary": r"(summary|profile|about)[\s\S]{0,1000}",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            sections[key] = match.group(0)

    return sections
