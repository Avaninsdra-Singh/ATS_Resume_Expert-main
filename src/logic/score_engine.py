import json
from pathlib import Path

from src.logic.synonym_matcher import match_with_synonyms


def _find_keywords_path() -> Path:
    this_file = Path(__file__).resolve()
    candidates = []

    if len(this_file.parents) >= 3:
        candidates.append(this_file.parents[2] / "constants" / "skill_keywords.json")
    if len(this_file.parents) >= 2:
        candidates.append(this_file.parents[1] / "constants" / "skill_keywords.json")
    if len(this_file.parents) >= 4:
        candidates.append(this_file.parents[3] / "constants" / "skill_keywords.json")

    candidates.extend([
        Path.cwd() / "constants" / "skill_keywords.json",
        Path.cwd() / "src" / "constants" / "skill_keywords.json",
    ])

    for path in candidates:
        if path.exists():
            return path

    raise FileNotFoundError(
        "Could not locate constants/skill_keywords.json. "
        "Checked: " + ", ".join(str(p) for p in candidates)
    )


KEYWORDS_PATH = _find_keywords_path()
with KEYWORDS_PATH.open("r", encoding="utf-8") as f:
    KEYWORDS = json.load(f)


def evaluate_resume(sections, jd_text):
    required_skills = KEYWORDS.get("skills", [])
    soft_skills = KEYWORDS.get("soft_skills", [])

    section_texts = [sections.get(section, "") or "" for section in ["education", "experience", "skills", "certifications", "projects", "summary"]]
    all_resume_text = " ".join(section_texts)

    matched_skills = match_with_synonyms(required_skills, all_resume_text)
    matched_soft_skills = match_with_synonyms(soft_skills, all_resume_text)

    # Simple point logic
    skill_score = len(matched_skills) / len(required_skills) * 50 if required_skills else 0
    soft_score = len(matched_soft_skills) / len(soft_skills) * 10 if soft_skills else 0
    experience_score = 20 if len(sections.get("experience", "") or "") > 100 else 0
    edu_score = 10 if len(sections.get("education", "") or "") > 50 else 0
    cert_score = 10 if len(sections.get("certifications", "") or "") > 50 else 0

    total = skill_score + soft_score + experience_score + edu_score + cert_score
    return round(total, 2), matched_skills, required_skills
