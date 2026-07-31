import json
import os
from typing import Dict, Any
from fastapi import HTTPException, status
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key or api_key.strip() in ("", "your-actual-groq-key-here", "your-key-here"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="GROQ_API_KEY is missing or not set correctly in .env file",
        )

    return Groq(api_key=api_key.strip())


def analyze_resume_and_jd(resume_text: str, job_description: str) -> Dict[str, Any]:
    """
    Calls Groq (Llama model) and returns structured skill-gap analysis.
    """
    client = get_groq_client()

    system_prompt = """
You are an expert career coach and technical recruiter for engineering students.
You must return ONLY valid JSON. No markdown, no explanation, no extra text.
"""

    user_prompt = f"""
Analyse the following resume against the job description.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Return a JSON object with exactly this structure:
{{
  "extracted_skills": {{
    "resume_skills": ["skill1", "skill2"],
    "job_required_skills": ["skill1", "skill2"],
    "matching_skills": ["skill1"],
    "missing_skills": ["skill1"]
  }},
  "gap_analysis": {{
    "summary": "2-3 sentence summary of the gap",
    "priority_skills_to_learn": [
      {{"skill": "name", "reason": "why important", "estimated_weeks": 2}}
    ],
    "strengths": ["strength1", "strength2"]
  }},
  "readiness_score": 65
}}

Rules:
- readiness_score must be an integer between 0 and 100
- Be realistic for an engineering student
- Prefer concrete technical skills
- Return ONLY the JSON object
"""

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # strong & free on Groq
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=1500,
        )

        raw_text = completion.choices[0].message.content.strip()

        # Remove markdown fences if the model adds them
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        data = json.loads(raw_text)

        # Safety
        if "readiness_score" not in data:
            data["readiness_score"] = 50
        data["readiness_score"] = max(0, min(100, int(data["readiness_score"])))

        return data

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Groq returned invalid JSON. Please try again.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error while calling Groq: {str(e)}",
        )