import json
from src.logic.synonym_matcher import match_with_synonyms

with open("constants/skill_keywords.json", "r") as f:
    KEYWORDS = json.load(f)

def evaluate_resume(sections, jd_text):
    required_skills = KEYWORDS["skills"]
    soft_skills = KEYWORDS["soft_skills"]

    all_resume_text = " ".join(sections.values()).lower()
    resume_words = all_resume_text.split()

    matched_skills = match_with_synonyms(required_skills, resume_words)
    matched_soft_skills = match_with_synonyms(soft_skills, resume_words)

    # Simple point logic
    skill_score = len(matched_skills) / len(required_skills) * 50
    soft_score = len(matched_soft_skills) / len(soft_skills) * 10
    experience_score = 20 if "experience" in sections and len(sections["experience"]) > 100 else 0
    edu_score = 10 if "education" in sections and len(sections["education"]) > 50 else 0
    cert_score = 10 if "certifications" in sections and len(sections["certifications"]) > 50 else 0

    total = skill_score + soft_score + experience_score + edu_score + cert_score
    return round(total, 2), matched_skills, required_skills
