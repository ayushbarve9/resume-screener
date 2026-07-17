"""Pydantic models for type safety, validation, and structured output parsing in FastAPI.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class CandidateEvaluation(BaseModel):
    candidate_name: str = Field(description="Candidate's full name extracted from the resume")
    target_position: str = Field(description="Target position / job title evaluated against")
    match_score: int = Field(description="Match score out of 100", ge=0, le=100)
    gap_analysis: str = Field(description="A brief paragraph summarizing how well the candidate matches the job description and the main gap")
    strengths: List[str] = Field(description="Top 3 key strengths of the candidate relative to the requirements")
    gaps: List[str] = Field(description="Top 3 critical gaps or missing qualifications of the candidate")
    interview_questions: List[str] = Field(description="Exactly 3 targeted, technical interview questions based on the candidate's gaps")
    resume_revisions: List[str] = Field(description="3 to 4 actionable resume revisions (e.g. key technical terms or project metrics to add)")

class ExecutiveSummary(BaseModel):
    winner_name: str = Field(description="The name of the top-recommended candidate. If only 1 candidate, set this to their name.")
    justification: str = Field(description="1-2 sentences explaining why this candidate is the best fit or summary of overall capability if only 1 candidate.")
    rankings: List[str] = Field(description="Ordered list of candidate names, ranked from best match to worst match.")
    trade_offs: List[str] = Field(description="Key trade-offs or comparison points between candidates (e.g. 'Candidate A has more coding experience but Candidate B has DevOps skills')")

class ScreeningResponse(BaseModel):
    evaluations: List[CandidateEvaluation] = Field(description="List of detailed evaluations for each candidate")
    executive_summary: ExecutiveSummary = Field(description="Recruitment verdict, ranking, winner selection, and trade-offs")

class ExtractionResult(BaseModel):
    filename: str = Field(description="The name of the uploaded file")
    text: str = Field(description="The extracted raw text content")
    page_count: int = Field(description="Number of pages in the document", ge=0)
    is_scanned: bool = Field(description="True if the PDF seems to contain scanned image pages with no extractable text")
    confidence_score: float = Field(description="Extraction confidence score from 0.0 (failed/empty) to 1.0 (perfectly parsed text)")
    error_message: Optional[str] = Field(default=None, description="Detailed error message if the extraction failed")
