import json
import re
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()  # reads your .env file automatically

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def _extract_json(text: str) -> str:
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1:
        return text[start : end + 1]
    return text


def _call_groq(prompt: str, max_tokens: int = 1000) -> str:
    client = Groq(api_key=GROQ_API_KEY)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def analyze_resume(resume_text: str, jd_text: str, api_key: str = None) -> dict:
    prompt = f"""You are an expert ATS (Applicant Tracking System) and resume analyst.

Analyze the resume against the job description and respond ONLY with a JSON object — no markdown, no preamble, no explanation.

Resume:
{resume_text}

Job Description:
{jd_text}

Respond with exactly this JSON structure:
{{
  "ats_score": <integer 0-100>,
  "matched_skills": [<list of skills found in both resume and JD>],
  "missing_skills": [<list of skills in JD but not in resume>],
  "bonus_skills": [<skills in resume relevant but not explicitly required>],
  "strengths": "<2-3 sentence summary of candidate strengths>",
  "gaps": "<2-3 sentence summary of gaps or missing experience>",
  "suggestions": "<2-3 actionable improvement suggestions for the resume>",
  "verdict": "<one of: Excellent Match | Strong Match | Good Match | Partial Match | Needs Improvement>"
}}"""
    raw = _call_groq(prompt, 1000)
    return json.loads(_extract_json(raw))


def score_for_ranking(resume_text: str, jd_text: str, api_key: str = None) -> dict:
    prompt = f"""You are an ATS system. Score this resume against the job description.
Respond ONLY with JSON: {{"ats_score": <integer 0-100>, "verdict": "<one short line>"}}

Resume: {resume_text}

Job Description: {jd_text}"""
    raw = _call_groq(prompt, 200)
    result = json.loads(_extract_json(raw))
    result["ats_score"] = max(0, min(100, int(result.get("ats_score", 0))))
    return result