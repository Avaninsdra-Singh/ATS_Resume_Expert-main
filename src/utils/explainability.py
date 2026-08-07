def show_explanation(score, matched, required):
    matched_set = set(matched)
    missing = [skill for skill in required if skill not in matched_set]
    return {
        "Score": score,
        "Matched Skills": matched,
        "Missing Skills": missing,
    }
