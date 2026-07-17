"""FastAPI entry point implementing REST API endpoints and static file hosting.
"""

import os
import json
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from models import ScreeningResponse
from extractors import extract_resume
from evaluator import evaluate_candidates
from report_generator import generate_docx_report

app = FastAPI(
    title="AI Resume Screening Dashboard API",
    description="Backend API serving the React candidate evaluation engine."
)

# Enable CORS for development environments (Vite local dev server port 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/screen")
async def screen_resumes(
    job_description: str = Form(...),
    model_name: str = Form(...),
    api_key: Optional[str] = Form(None),
    resumes: List[UploadFile] = File(...)
):
    """Process uploaded resumes, extract text, call Gemini, and return candidate scores."""
    # Retrieve API Key from env if not provided
    effective_api_key = api_key if api_key and api_key.strip() else (
        os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    )
    
    if not effective_api_key:
        raise HTTPException(
            status_code=400,
            detail="Google Gemini API key is missing. Please provide it in the UI settings or set GOOGLE_API_KEY in the environment."
        )


    if not resumes:
        raise HTTPException(
            status_code=400,
            detail="At least one resume file must be uploaded."
        )

    processed_candidates = []
    metadata_map = {}
    extraction_errors = []

    # 1. Extraction phase
    for upload_file in resumes:
        try:
            file_bytes = await upload_file.read()
            ext_result = extract_resume(upload_file.filename, file_bytes)
            
            if ext_result.error_message:
                extraction_errors.append({
                    "filename": upload_file.filename,
                    "error": ext_result.error_message
                })
            else:
                processed_candidates.append({
                    "filename": ext_result.filename,
                    "text": ext_result.text
                })
                metadata_map[ext_result.filename] = {
                    "page_count": ext_result.page_count,
                    "is_scanned": ext_result.is_scanned,
                    "confidence_score": ext_result.confidence_score,
                    "text": ext_result.text[:10000]  # Cap raw text preview to 10k chars
                }
        except Exception as e:
            extraction_errors.append({
                "filename": upload_file.filename,
                "error": str(e)
            })

    if not processed_candidates:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to parse text from any uploaded files. Errors: {json.dumps(extraction_errors)}"
        )

    # 2. Evaluation phase via Gemini API
    try:
        screening_res, was_cached = evaluate_candidates(
            api_key=effective_api_key,
            model_name=model_name,
            job_description=job_description,
            candidates_list=processed_candidates
        )
        
        return {
            "success": True,
            "response": screening_res.model_dump(),
            "was_cached": was_cached,
            "metadata": metadata_map,
            "warnings": extraction_errors
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gemini API screening failed: {str(e)}"
        )

@app.post("/api/export/docx")
async def export_docx(
    job_title: str = Form(...),
    screening_response_json: str = Form(...)
):
    """Generate and return a styled Word Document (.docx) report from evaluation response."""
    try:
        response_data = json.loads(screening_response_json)
        response_model = ScreeningResponse(**response_data)
        
        doc_bio = generate_docx_report(response_model, job_title)
        
        return StreamingResponse(
            doc_bio,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=ATS_Candidate_Evaluation_Report.docx"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Word document generation failed: {str(e)}"
        )

# Mount local static folder serving Single-Page HTML Dashboard directly
static_dir_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "static")
)

@app.get("/")
def serve_frontend_root():
    index_file = os.path.join(static_dir_path, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "status": "API is running.",
        "message": "HTML dashboard frontend file 'static/index.html' not found."
    }

