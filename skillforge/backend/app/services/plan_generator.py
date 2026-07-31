import json
import os
from typing import Dict, Any, List
from fastapi import HTTPException, status
from dotenv import load_dotenv

load_dotenv()


def _mock_weekly_plan(missing_skills: List[str], readiness_score: float) -> Dict[str, Any]:
    """High-quality fallback plan when AI is unavailable."""
    priority = missing_skills[:5] if missing_skills else ["FastAPI", "PostgreSQL", "Docker", "REST APIs", "System Design"]

    weeks = []
    for i, skill in enumerate(priority, start=1):
        weeks.append({
            "week": i,
            "focus_skill": skill,
            "daily_hours": 2,
            "tasks": [
                f"Learn core concepts of {skill} (official docs + 1 tutorial)",
                f"Build a small mini-project using {skill}",
                "Write notes + revise previous skills",
                "Solve 3-5 related practice problems"
            ],
            "resources": [
                f"Official {skill} documentation",
                "Free YouTube crash course",
                "One good paid course (optional)"
            ],
            "estimated_cost_inr": 0 if i <= 2 else 499
        })

    total_budget = sum(w["estimated_cost_inr"] for w in weeks)

    return {
        "title": f"8-Week Backend Readiness Plan (Score: {readiness_score})",
        "duration_weeks": len(weeks),
        "total_hours": len(weeks) * 14,          # 2 hrs × 7 days
        "recommended_budget_inr": total_budget,
        "weekly_plan": weeks,
        "tips": [
            "Study 2 focused hours daily instead of long irregular sessions",
            "Build one small project every week – projects beat certificates",
            "Track expenses in SkillForge so you know real ROI",
            "Revise previous week’s skill every Sunday"
        ]
    }


def generate_weekly_plan(
    missing_skills: List[str],
    readiness_score: float,
    resume_summary: str = "",
) -> Dict[str, Any]:
    """
    Generate a realistic weekly learning plan + budget.
    Tries Groq first. Falls back to high-quality mock if key is missing or fails.
    """
    api_key = os.getenv("GROQ_API_KEY")

    # Fallback to mock if no key
    if not api_key or api_key.strip() in ("", "your-actual-groq-key-here"):
        return _mock_weekly_plan(missing_skills, readiness_score)

    try:
        from groq import Groq
        client = Groq(api_key=api_key.strip())

        prompt = f"""
You are an expert career coach for engineering students in India.
Create a realistic weekly learning plan.

Current readiness score: {readiness_score}
Missing skills: {', '.join(missing_skills[:8])}

Return ONLY valid JSON with this exact structure:
{{
  "title": "string",
  "duration_weeks": 6,
  "total_hours": 84,
  "recommended_budget_inr": 2000,
  "weekly_plan": [
    {{
      "week": 1,
      "focus_skill": "FastAPI",
      "daily_hours": 2,
      "tasks": ["task1", "task2", "task3"],
      "resources": ["resource1", "resource2"],
      "estimated_cost_inr": 0
    }}
  ],
  "tips": ["tip1", "tip2"]
}}

Rules:
- Maximum 8 weeks
- daily_hours between 1.5 and 3
- Keep budget realistic for Indian students (prefer free resources)
- Return ONLY the JSON
"""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1800,
        )

        raw = completion.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()

        data = json.loads(raw)
        return data

    except Exception:
        # Any failure → safe mock
        return _mock_weekly_plan(missing_skills, readiness_score)