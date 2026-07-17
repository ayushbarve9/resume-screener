"""Configuration settings and constants for the AI Resume Screening Backend.
"""
import os

# Model selection mapping
DEFAULT_MODELS = {
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
