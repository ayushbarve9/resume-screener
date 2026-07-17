"""Gemini API evaluator logic utilizing gemini-3.1-flash-lite, persistent file-based caching, and tenacity retries.
"""

import json
import os
import hashlib
import threading
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE, RETRY_SETTINGS, CACHE_FILE_PATH
from models import ScreeningResponse

# Threading lock for thread-safe persistent file cache operations
_cache_lock = threading.Lock()
_cache_data = {}

def _load_cache():
    """Load persistent cache file from disk."""
    global _cache_data
    with _cache_lock:
        if os.path.exists(CACHE_FILE_PATH):
            try:
                with open(CACHE_FILE_PATH, "r", encoding="utf-8") as f:
                    _cache_data = json.load(f)
            except Exception:
                _cache_data = {}
        else:
            _cache_data = {}

def _save_cache():
    """Save persistent cache data to disk."""
    with _cache_lock:
        try:
            with open(CACHE_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(_cache_data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

# Initialize cache at import time
_load_cache()

def _get_api_client(api_key: str) -> genai.Client:
    """Create a genai Client."""
    if api_key:
        return genai.Client(api_key=api_key)
    return genai.Client()

@retry(
    stop=stop_after_attempt(RETRY_SETTINGS["max_attempts"]),
    wait=wait_exponential(
        multiplier=RETRY_SETTINGS["min_seconds"],
        min=RETRY_SETTINGS["min_seconds"],
        max=RETRY_SETTINGS["max_seconds"]
    ),
    retry=retry_if_exception_type(APIError),
    reraise=True
)
def _execute_api_call(api_key: str, model_name: str, user_prompt: str) -> str:
    """Execute API content generation with structured outputs constraints."""
    client = _get_api_client(api_key)
    
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_schema=ScreeningResponse,
        temperature=0.1
    )
    
    response = client.models.generate_content(
        model=model_name,
        contents=user_prompt,
        config=config
    )
    
    if not response.text:
        raise ValueError("Received empty response from Gemini API.")
        
    return response.text

def evaluate_candidates(
    api_key: str,
    model_name: str,
    job_description: str,
    candidates_list: list[dict]
) -> tuple[ScreeningResponse, bool]:
    """Perform resume screening evaluation against JD using persistent local file cache and Gemini API."""
    
    # 1. Structure candidates string
    candidates_repr = []
    for cand in candidates_list:
        candidates_repr.append(
            f"=== CANDIDATE FILE: {cand['filename']} ===\n{cand['text']}\n"
        )
    candidates_data = "\n".join(candidates_repr)
    
    # 2. Build User Prompt
    user_prompt = USER_PROMPT_TEMPLATE.format(
        job_description=job_description,
        candidates_data=candidates_data
    )
    
    # 3. Create unique query hash key
    key_source = f"{model_name}:{job_description}:{candidates_data}"
    query_key = hashlib.sha256(key_source.encode('utf-8')).hexdigest()
    
    # 4. Check memory/persistent cache
    was_cached = False
    raw_json_response = None
    
    if query_key in _cache_data:
        raw_json_response = _cache_data[query_key]
        was_cached = True
    else:
        # Call API
        raw_json_response = _execute_api_call(api_key, model_name, user_prompt)
        # Store in cache
        _cache_data[query_key] = raw_json_response
        _save_cache()
        
    # 5. Parse JSON string to Pydantic object
    try:
        data = json.loads(raw_json_response)
        parsed_response = ScreeningResponse(**data)
        return parsed_response, was_cached
    except Exception as e:
        # If parsing fails, remove key from cache so we don't store bad output
        if not was_cached and query_key in _cache_data:
            del _cache_data[query_key]
            _save_cache()
            
        raise ValueError(
            f"Failed to parse structured JSON response from Gemini API: {str(e)}\n"
            f"Raw Response: {raw_json_response}"
        )
