import json
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

_HAS_GEMINI = False
_HAS_OPENAI = False

genai = None
openai = None
_openai_client = None

def get_ai_configuration():
    return {
        "openai_api_key_set": bool(OPENAI_API_KEY),
        "gemini_api_key_set": bool(GEMINI_API_KEY),
        "openai_model": OPENAI_MODEL,
        "gemini_model": GEMINI_MODEL,
        "openai_installed": _HAS_OPENAI,
        "gemini_installed": _HAS_GEMINI,
    }

try:
    import google.generativeai as genai_module

    genai = genai_module
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    _HAS_GEMINI = True
except Exception:
    _HAS_GEMINI = False

try:
    import openai as openai_module

    openai = openai_module
    if OPENAI_API_KEY:
        if hasattr(openai_module, "OpenAI"):
            _openai_client = openai_module.OpenAI(api_key=OPENAI_API_KEY)
        elif hasattr(openai_module, "ChatCompletion"):
            openai_module.api_key = OPENAI_API_KEY
            _openai_client = openai_module
        _HAS_OPENAI = True
except Exception:
    _HAS_OPENAI = False


def _build_prompt(resume_text, job_description):
    return f"""
Compare the following resume with the job description. Give a score out of 100 and explain the strengths and gaps.

Job Description:
{job_description}

Resume:
{resume_text}

Respond ONLY in this exact JSON format:
{{
    "score": <int>,
    "strengths": ["..."],
    "gaps": ["..."]
}}
"""


def _extract_response_content(response):
    if hasattr(response, "choices") and getattr(response, "choices", None):
        choice = response.choices[0]
        message = getattr(choice, "message", None)
        if message is not None:
            content = getattr(message, "content", None)
            if isinstance(content, list):
                parts = []
                for item in content:
                    if isinstance(item, dict):
                        text_value = item.get("text") or item.get("content") or ""
                        if text_value:
                            parts.append(str(text_value))
                    elif item:
                        parts.append(str(item))
                return "".join(parts).strip()
            return str(content).strip()

    if hasattr(response, "output_text"):
        return str(response.output_text).strip()

    if hasattr(response, "text"):
        return str(response.text).strip()

    return str(response).strip()


def parse_ai_response(result):
    if isinstance(result, dict):
        payload = dict(result)
        strengths = payload.get("strengths", [])
        gaps = payload.get("gaps", [])
        if not isinstance(strengths, list):
            strengths = []
        if not isinstance(gaps, list):
            gaps = []
        return {"score": payload.get("score", 0), "strengths": strengths, "gaps": gaps, "error": payload.get("error")}

    if isinstance(result, str):
        cleaned = result.strip()
        if not cleaned:
            return {"score": 0, "strengths": [], "gaps": [], "error": "Empty AI response"}
        if cleaned.lower().startswith("error:"):
            return {"score": 0, "strengths": [], "gaps": [], "error": cleaned}

        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            return {"score": 0, "strengths": [], "gaps": [cleaned], "error": f"Could not parse AI response: {cleaned}"}

        return parse_ai_response(parsed)

    return {"score": 0, "strengths": [], "gaps": [], "error": f"Unsupported AI response type: {type(result).__name__}"}


def _call_gemini(prompt):
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    return response.text.strip()


def _call_openai(prompt):
    if _openai_client is None:
        raise RuntimeError("OpenAI client is not configured")

    if hasattr(_openai_client, "chat") and hasattr(_openai_client.chat, "completions"):
        response = _openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        return _extract_response_content(response)

    if hasattr(_openai_client, "responses") and hasattr(_openai_client.responses, "create"):
        response = _openai_client.responses.create(
            model=OPENAI_MODEL,
            input=prompt,
            temperature=0.2,
            max_output_tokens=600,
        )
        return _extract_response_content(response)

    if hasattr(_openai_client, "ChatCompletion") and hasattr(_openai_client.ChatCompletion, "create"):
        response = _openai_client.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        return _extract_response_content(response)

    raise RuntimeError("Unsupported OpenAI client interface")


def get_ai_evaluation(resume_text, job_description):
    prompt = _build_prompt(resume_text, job_description)

    if OPENAI_API_KEY and _HAS_OPENAI:
        try:
            return parse_ai_response(_call_openai(prompt))
        except Exception as e:
            return {"score": 0, "strengths": [], "gaps": [], "error": f"OpenAI evaluation failed: {e}"}

    if GEMINI_API_KEY and _HAS_GEMINI:
        try:
            return parse_ai_response(_call_gemini(prompt))
        except Exception as e:
            return {"score": 0, "strengths": [], "gaps": [], "error": f"Gemini evaluation failed: {e}"}

    if not OPENAI_API_KEY and not GEMINI_API_KEY:
        return {"score": 0, "strengths": [], "gaps": [], "error": "No AI API key configured. Set OPENAI_API_KEY or GEMINI_API_KEY in your .env file."}

    return {"score": 0, "strengths": [], "gaps": [], "error": "AI provider not available. Install openai or google.generativeai and configure an API key."}
