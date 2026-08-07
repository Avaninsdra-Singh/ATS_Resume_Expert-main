import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

def get_ai_evaluation(resume_text, job_description):
    prompt = f"""
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

    try:
        # ✅ Use Gemini 1.5 model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error: {str(e)}"
