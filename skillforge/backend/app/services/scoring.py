from typing import Dict, Any, List


def calculate_readiness_score(
    matching_skills: List[str],
    missing_skills: List[str],
    current_levels: Dict[str, int] | None = None,
) -> Dict[str, Any]:
    """
    Transparent readiness scoring.

    Formula (simple & explainable):
    - Base score from skill coverage
    - Bonus for high current levels on matching skills
    - Penalty for critical missing skills

    Returns score (0-100) + breakdown so the UI can show "why this score".
    """
    total_required = len(matching_skills) + len(missing_skills)
    if total_required == 0:
        return {
            "score": 0,
            "coverage": 0.0,
            "matching_count": 0,
            "missing_count": 0,
            "breakdown": "No skills found to evaluate.",
        }

    matching_count = len(matching_skills)
    missing_count = len(missing_skills)

    # 1. Coverage component (0-70 points)
    coverage = matching_count / total_required
    coverage_score = coverage * 70

    # 2. Level bonus (0-20 points) – only if we have current levels
    level_bonus = 0.0
    if current_levels and matching_skills:
        levels = [current_levels.get(skill, 50) for skill in matching_skills]
        avg_level = sum(levels) / len(levels)
        level_bonus = (avg_level / 100) * 20

    # 3. Critical missing penalty (0-10 points deducted)
    critical_keywords = ["fastapi", "django", "postgresql", "docker", "system design", "rest"]
    critical_missing = sum(
        1 for s in missing_skills if any(k in s.lower() for k in critical_keywords)
    )
    penalty = min(critical_missing * 2.5, 10)

    raw_score = coverage_score + level_bonus - penalty
    final_score = max(0, min(100, round(raw_score)))

    breakdown = (
        f"Coverage: {matching_count}/{total_required} skills matched → {coverage_score:.1f} pts. "
        f"Level bonus: {level_bonus:.1f} pts. "
        f"Critical missing penalty: -{penalty:.1f} pts."
    )

    return {
        "score": final_score,
        "coverage": round(coverage * 100, 1),
        "matching_count": matching_count,
        "missing_count": missing_count,
        "breakdown": breakdown,
    }