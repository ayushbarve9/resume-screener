"""Text extraction logic for PDF and DOCX files with validation and LRU caching.
"""

import functools
import hashlib
import io
import re
import PyPDF2
from docx import Document
from models import ExtractionResult

def get_bytes_hash(file_bytes: bytes) -> str:
    """Generate MD5 hash of file bytes for caching keys."""
    return hashlib.md5(file_bytes).hexdigest()

def normalize_text(text: str) -> str:
    """Normalize whitespaces, clean control characters and normalize encoding."""
    if not text:
        return ""
    text = text.replace("\x00", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_pdf_text_internal(file_bytes: bytes) -> tuple[str, int, bool, float]:
    """Helper to extract text from PDF file bytes."""
    file_like = io.BytesIO(file_bytes)
    try:
        reader = PyPDF2.PdfReader(file_like)
        page_count = len(reader.pages)
        if page_count == 0:
            return "", 0, False, 0.0

        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
        
        normalized = normalize_text(extracted_text)
        
        is_scanned = False
        confidence = 1.0
        
        if len(normalized) < 50:
            is_scanned = True
            confidence = 0.1
        else:
            char_per_page = len(normalized) / page_count
            if char_per_page < 100:
                is_scanned = True
                confidence = 0.3
            elif char_per_page < 300:
                confidence = 0.7
                
        return normalized, page_count, is_scanned, confidence
        
    except PyPDF2.errors.PdfReadError as pe:
        raise Exception(f"The PDF file is corrupted or encrypted: {str(pe)}")
    except Exception as e:
        raise Exception(f"Failed to read PDF structure: {str(e)}")

def extract_docx_text_internal(file_bytes: bytes) -> tuple[str, int, bool, float]:
    """Helper to extract text from DOCX file bytes."""
    file_like = io.BytesIO(file_bytes)
    try:
        doc = Document(file_like)
        paragraphs_text = [p.text for p in doc.paragraphs if p.text]
        
        table_text = []
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text:
                        table_text.append(cell.text)
                        
        combined_text = "\n".join(paragraphs_text + table_text)
        normalized = normalize_text(combined_text)
        
        page_count = 1
        is_scanned = False
        confidence = 1.0 if len(normalized) > 50 else 0.5
        
        return normalized, page_count, is_scanned, confidence
        
    except Exception as e:
        raise Exception(f"Failed to read DOCX structure: {str(e)}")

@functools.lru_cache(maxsize=256)
def extract_text_cached(file_bytes: bytes, filename: str) -> dict:
    """Cached function that handles parsing based on file extension.
    
    Uses standard functools.lru_cache for fast memory retrieval.
    """
    ext = filename.split(".")[-1].lower()
    
    # Input validation
    if len(file_bytes) == 0:
        return {
            "filename": filename,
            "text": "",
            "page_count": 0,
            "is_scanned": False,
            "confidence_score": 0.0,
            "error_message": "Uploaded file is empty (0 bytes)."
        }
        
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB limit
        return {
            "filename": filename,
            "text": "",
            "page_count": 0,
            "is_scanned": False,
            "confidence_score": 0.0,
            "error_message": "Uploaded file exceeds the 10MB size limit."
        }

    try:
        if ext == "pdf":
            text, page_count, is_scanned, confidence = extract_pdf_text_internal(file_bytes)
        elif ext == "docx":
            text, page_count, is_scanned, confidence = extract_docx_text_internal(file_bytes)
        elif ext in ["txt", "text", "md"]:
            raw_text = file_bytes.decode("utf-8", errors="ignore")
            text = normalize_text(raw_text)
            page_count = max(1, len(text) // 2200 + 1)
            is_scanned = False
            confidence = 1.0
        else:
            return {
                "filename": filename,
                "text": "",
                "page_count": 0,
                "is_scanned": False,
                "confidence_score": 0.0,
                "error_message": f"Unsupported file format: '.{ext}'. Supported formats: .pdf, .docx, .txt"
            }
            
        return {
            "filename": filename,
            "text": text,
            "page_count": page_count,
            "is_scanned": is_scanned,
            "confidence_score": confidence,
            "error_message": None
        }
    except Exception as e:
        return {
            "filename": filename,
            "text": "",
            "page_count": 0,
            "is_scanned": False,
            "confidence_score": 0.0,
            "error_message": str(e)
        }

def extract_resume(filename: str, file_bytes: bytes) -> ExtractionResult:
    """Extract text and return as Pydantic ExtractionResult."""
    result_dict = extract_text_cached(file_bytes, filename)
    return ExtractionResult(**result_dict)
