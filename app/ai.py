import json
import re
import httpx
from pydantic import BaseModel, Field
from .config import OLLAMA_MODEL, OLLAMA_URL


class JobData(BaseModel):
    company: str = ''
    role: str = ''
    location: str = ''
    skills: list[str] = Field(default_factory=list)
    experience: str = ''
    education: str = ''
    apply_url: str = ''
    hr_email: str = ''
    description: str = ''


class MatchResult(BaseModel):
    score: int
    reasons: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)


class ResumeData(BaseModel):
    summary: str
    skills: list[str]
    experience: list[dict]
    projects: list[dict]
    education: str


async def ollama_chat(prompt):
    payload = {
        'model': OLLAMA_MODEL,
        'messages': [{'role': 'user', 'content': prompt}],
        'stream': False
    }
    async with httpx.AsyncClient(timeout=180) as client:
        response = await client.post(f'{OLLAMA_URL}/api/chat', json=payload)
        response.raise_for_status()
        return response.json()['message']['content']


def extract_json(text):
    text = text.strip()
    text = re.sub(r'^```(?:json)?\\s*', '', text)
    text = re.sub(r'\\s*```$', '', text)
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError('Model did not return a JSON object.')
    return json.loads(text[start:end + 1])


async def extract_job(raw_post):
    prompt = f'''Extract this Telegram job post into JSON.
Return ONLY valid JSON with this schema:
{{
  "company": "",
  "role": "",
  "location": "",
  "skills": [],
  "experience": "",
  "education": "",
  "apply_url": "",
  "hr_email": "",
  "description": ""
}}
Never invent information. URLs and email addresses must come from the input.

JOB POST:\n{raw_post}'''
    return JobData.model_validate(extract_json(await ollama_chat(prompt)))


async def score_job(job, profile):
    prompt = f'''Evaluate this candidate for this job.

JOB:\n{job.model_dump_json(indent=2)}

MASTER PROFILE:\n{profile}

Return ONLY JSON:
{{
  "score": 0,
  "reasons": [],
  "missing_requirements": []
}}
Score 0-100. Do not assume unsupported skills or experience.'''
    return MatchResult.model_validate(extract_json(await ollama_chat(prompt)))


async def tailor_resume(job, profile):
    prompt = f'''Create a truthful ATS-friendly resume configuration.

JOB:\n{job.model_dump_json(indent=2)}

MASTER PROFILE:\n{profile}

Return ONLY JSON:
{{
  "summary": "",
  "skills": [],
  "experience": [],
  "projects": [],
  "education": ""
}}

Rules:
1. The master profile is the only source of candidate facts.
2. Never invent employers, roles, projects, technologies, metrics, dates, degrees, certifications, or responsibilities.
3. You may reorder, shorten, and rewrite facts that already exist.
4. Prefer genuinely supported job keywords.
5. Never claim a missing skill merely because it is in the JD.
6. Keep it compact for one page.'''
    return ResumeData.model_validate(extract_json(await ollama_chat(prompt)))
