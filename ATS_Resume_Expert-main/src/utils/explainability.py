def show_explanation(score, matched, required):
    missing = list(set(required) - set(matched))
    return {
        "Score": score,
        "Matched Skills": matched,
        "Missing Skills": missing
    }
