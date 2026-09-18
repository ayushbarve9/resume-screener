"""Configuration settings and constants for the AI Resume Screening Backend.
"""
import os

# Auto-load .env if available
def _load_env_file():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("\"'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

_load_env_file()

# Model selection mapping
DEFAULT_MODELS = {
    "Gemini 2.5 Flash (Recommended)": "gemini-2.5-flash",
    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 1.5 Flash": "gemini-1.5-flash",
    "Gemini 1.5 Pro": "gemini-1.5-pro",
    "Gemini 3.1 Flash-Lite": "gemini-3.1-flash-lite"
}

# Score threshold settings
DEFAULT_THRESHOLDS = {
    "high": 80,
    "medium": 60
}

# API Retry Configuration
RETRY_SETTINGS = {
    "max_attempts": 3,
    "min_seconds": 2,
    "max_seconds": 10
}

# Cache Configuration
CACHE_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "evaluation_cache.json"
)

# Evaluation System Prompt
SYSTEM_PROMPT = """You are an elite corporate technical recruiter and strict ATS evaluation engine.
Your task is to analyze candidate resumes against a provided Job Description and output precise, objective evaluations in structured JSON format.
Be critical and direct. Do not sugarcoat candidate scores. If a skill or requirement is not explicitly present or implied by high-quality experience in the resume, treat it as a gap.
"""

# Evaluation User Prompt Templates
USER_PROMPT_TEMPLATE = """Evaluate the candidate resumes against the Job Description.

TARGET JOB DESCRIPTION:
{job_description}

CANDIDATES TO PROCESS:
{candidates_data}

INSTRUCTION:
Evaluate each candidate's suitability for this role.
Provide a clear Match Score (0 to 100) based on how well they meet the requirements.
List their top 3 strengths, top 3 gaps, 3 tailored interview questions to verify gaps, and 3-4 actionable resume revisions (specific keywords or phrasing changes).

If there are multiple candidates, you must also provide an executive summary highlighting rankings, selecting a clear winner with a short justification, and detailing the key trade-offs between them.
"""
