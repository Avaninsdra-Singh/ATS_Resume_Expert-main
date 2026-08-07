def evaluate_quality(sections):
    score = 0
    if len(sections["summary"]) > 100:
        score += 20
    if len(sections["projects"]) > 100:
        score += 20
    if len(sections["skills"]) > 50:
        score += 20
    if len(sections["experience"]) > 100:
        score += 20
    if len(sections["education"]) > 50:
        score += 20
    return score
