import re


SECTION_PATTERNS = {
    "education": ["education", "academics", "academic background"],
    "experience": ["experience", "work history", "employment", "professional experience", "work experience"],
    "skills": ["skills", "technologies", "tools", "technical skills"],
    "certifications": ["certifications", "certificates", "licenses"],
    "projects": ["projects", "portfolio", "selected projects"],
    "summary": ["summary", "profile", "about", "professional summary"],
}


def _normalize_header(line):
    return re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()


def extract_resume_sections(text):
    sections = {
        "education": "",
        "experience": "",
        "skills": "",
        "certifications": "",
        "projects": "",
        "summary": "",
    }

    if not text:
        return sections

    lines = text.splitlines()
    header_positions = []

    for index, line in enumerate(lines):
        normalized = _normalize_header(line)
        if not normalized:
            continue
        for section_name, patterns in SECTION_PATTERNS.items():
            if any(pattern in normalized for pattern in patterns):
                header_positions.append((index, section_name))
                break

    header_positions.sort(key=lambda item: item[0])

    for idx, (line_index, section_name) in enumerate(header_positions):
        next_index = header_positions[idx + 1][0] if idx + 1 < len(header_positions) else len(lines)
        section_lines = [lines[line_index].strip()]
        section_lines.extend(line.strip() for line in lines[line_index + 1:next_index] if line.strip())
        sections[section_name] = "\n".join(section_lines).strip()

    return sections