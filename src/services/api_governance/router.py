"""
API Governance Service - REST API Router (Production Ready)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import tempfile
import os
import logging
import uuid

from src.services.api_governance.ingestion import get_ingestion_service
from src.services.api_governance.validator import get_validator_service
from src.services.api_governance.corrector import get_corrector_service
from src.core.exceptions import (
    PDFProcessingError,
    FileSizeExceededError,
    UnsupportedFileTypeError,
    InvalidSpecificationError,
    ValidationError,
    CorrectionError
)

router = APIRouter()
logger = logging.getLogger(__name__)

# Constants
MAX_SPEC_SIZE = 1 * 1024 * 1024  # 1 MB for spec content
SUPPORTED_SPEC_FORMATS = ["json", "yaml"]


# Request/Response Models with Validation
class ValidateRequest(BaseModel):
    """Validation request with input validation"""
    spec_content: str = Field(..., description="API specification content", min_length=1, max_length=MAX_SPEC_SIZE)
    spec_format: str = Field(default="json", description="Specification format (json/yaml)")
    
    @validator('spec_format')
    def validate_format(cls, v):
        if v.lower() not in SUPPORTED_SPEC_FORMATS:
            raise ValueError(f"Format must be one of: {', '.join(SUPPORTED_SPEC_FORMATS)}")
        return v.lower()


class ValidateResponse(BaseModel):
    """Validation response"""
    valid: bool
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1")
    violations: List[Dict[str, Any]]
    rules_checked: int
    features_analyzed: int
    request_id: str


class CorrectRequest(BaseModel):
    """Correction request with input validation"""
    spec_content: str = Field(..., description="API specification content", min_length=1, max_length=MAX_SPEC_SIZE)
    violations: List[Dict[str, Any]] = Field(..., description="Violations to correct", min_items=1)
    spec_format: str = Field(default="json", description="Specification format (json/yaml)")
    
    @validator('spec_format')
    def validate_format(cls, v):
        if v.lower() not in SUPPORTED_SPEC_FORMATS:
            raise ValueError(f"Format must be one of: {', '.join(SUPPORTED_SPEC_FORMATS)}")
        return v.lower()


class CorrectResponse(BaseModel):
    """Correction response"""
    corrected: bool
    corrected_spec: str
    changes: List[Dict[str, Any]]
    violations_fixed: int
    request_id: str


class IngestionResponse(BaseModel):
    """Ingestion response"""
    success: bool
    document: str
    doc_hash: str
    chunks_created: int
    page_count: int
    ids: List[str]
    total_ids: int
    duration_seconds: float
    request_id: str


class SuggestionRequest(BaseModel):
    """Suggestion request"""
    spec_content: str = Field(..., description="API specification content", min_length=1, max_length=MAX_SPEC_SIZE)
    spec_format: str = Field(default="json", description="Specification format (json/yaml)")
    
    @validator('spec_format')
    def validate_format(cls, v):
        if v.lower() not in SUPPORTED_SPEC_FORMATS:
            raise ValueError(f"Format must be one of: {', '.join(SUPPORTED_SPEC_FORMATS)}")
        return v.lower()


class SuggestionResponse(BaseModel):
    """Suggestion response"""
    suggestions: List[Dict[str, Any]]
    total_suggestions: int
    request_id: str


# Endpoints
@router.post("/ingest", response_model=IngestionResponse, status_code=200)
async def ingest_governance_document(
    request: Request,
    file: UploadFile = File(..., description="PDF document containing governance rules"),
    metadata: Optional[str] = None  # JSON string of additional metadata
):
    """
    Ingest a governance document (PDF) into the vector database.
    
    This endpoint:
    1. Validates the uploaded file
    2. Extracts text from the PDF
    3. Splits into chunks
    4. Generates embeddings
    5. Stores in vector database
    
    **File Requirements:**
    - Format: PDF only
    - Max Size: 50 MB
    - Max Pages: 1000
    
    **Returns:**
    - Document hash for deduplication
    - Number of chunks created
    - List of chunk IDs (first 10)
    - Processing duration
    """
    request_id = f"ing_{uuid.uuid4().hex[:8]}"
    
    logger.info(
        f"[{request_id}] Received ingestion request",
        extra={"filename": file.filename, "content_type": file.content_type}
    )
    
    # Validate file type
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise UnsupportedFileTypeError(
            file_type=file.filename.split('.')[-1] if file.filename else "unknown",
            supported_types=[".pdf"]
        )
    
    # Save uploaded file temporarily
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', mode='wb') as tmp:
            content = await file.read()
            
            # Check file size
            file_size = len(content)
            if file_size > 50 * 1024 * 1024:  # 50 MB
                raise FileSizeExceededError(
                    max_size=50 * 1024 * 1024,
                    actual_size=file_size
                )
            
            if file_size == 0:
                raise PDFProcessingError(
                    "Uploaded file is empty",
                    details={"filename": file.filename, "request_id": request_id}
                )
            
            tmp.write(content)
            tmp_path = tmp.name
        
        # Parse metadata if provided
        doc_metadata = {}
        if metadata:
            try:
                import json
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(
                    f"[{request_id}] Invalid metadata JSON, ignoring",
                    extra={"metadata": metadata}
                )
        
        # Ingest the document
        ingestion_service = get_ingestion_service()
        result = await ingestion_service.ingest_pdf(
            pdf_path=tmp_path,
            metadata=doc_metadata,
            request_id=request_id
        )
        
        logger.info(
            f"[{request_id}] Ingestion completed successfully",
            extra={"chunks": result.get("chunks_created"), "document": result.get("document")}
        )
        
        return result
    
    except (PDFProcessingError, FileSizeExceededError, UnsupportedFileTypeError):
        # Re-raise known exceptions
        raise
    
    except Exception as e:
        logger.error(
            f"[{request_id}] Unexpected error during ingestion",
            extra={"error": str(e), "filename": file.filename},
            exc_info=True
        )
        raise PDFProcessingError(
            f"Failed to ingest document: {str(e)}",
            details={"filename": file.filename, "request_id": request_id}
        )
    
    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"[{request_id}] Failed to delete temp file: {e}")


@router.post("/validate", response_model=ValidateResponse, status_code=200)
async def validate_api_spec(request: Request, validate_req: ValidateRequest):
    """
    Validate an API specification against governance rules.
    
    This endpoint:
    1. Parses the API specification (OpenAPI/Swagger)
    2. Retrieves relevant governance rules from vector DB
    3. Uses LLM to check for violations
    4. Returns compliance score and detailed violations
    
    **Supported Formats:**
    - OpenAPI 3.0+ (JSON/YAML)
    - Swagger 2.0 (JSON/YAML)
    
    **Returns:**
    - Compliance score (0.0 - 1.0)
    - List of violations with severity
    - Number of rules checked
    """
    request_id = f"val_{uuid.uuid4().hex[:8]}"
    
    logger.info(
        f"[{request_id}] Received validation request",
        extra={"format": validate_req.spec_format, "spec_length": len(validate_req.spec_content)}
    )
    
    try:
        validator_service = get_validator_service()
        result = await validator_service.validate_spec(
            spec_content=validate_req.spec_content,
            spec_format=validate_req.spec_format
        )
        
        logger.info(
            f"[{request_id}] Validation completed",
            extra={
                "valid": result.get("valid"),
                "score": result.get("compliance_score"),
                "violations": len(result.get("violations", []))
            }
        )
        
        result["request_id"] = request_id
        return result
    
    except Exception as e:
        logger.error(
            f"[{request_id}] Validation failed",
            extra={"error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise ValidationError(
            f"Failed to validate specification: {str(e)}",
            details={"request_id": request_id, "error_type": type(e).__name__}
        )


@router.post("/correct", response_model=CorrectResponse, status_code=200)
async def correct_violations(request: Request, correct_req: CorrectRequest):
    """
    Automatically correct violations in an API specification.
    
    This endpoint:
    1. Takes the API spec and list of violations
    2. Uses LLM to generate corrections
    3. Returns corrected specification
    4. Provides detailed change log
    
    **Note:** Review all changes before applying to production specs.
    
    **Returns:**
    - Corrected specification
    - List of changes made
    - Number of violations fixed
    """
    request_id = f"cor_{uuid.uuid4().hex[:8]}"
    
    logger.info(
        f"[{request_id}] Received correction request",
        extra={
            "format": correct_req.spec_format,
            "violations_count": len(correct_req.violations)
        }
    )
    
    try:
        corrector_service = get_corrector_service()
        result = await corrector_service.correct_violations(
            spec_content=correct_req.spec_content,
            violations=correct_req.violations,
            spec_format=correct_req.spec_format
        )
        
        logger.info(
            f"[{request_id}] Correction completed",
            extra={
                "corrected": result.get("corrected"),
                "violations_fixed": result.get("violations_fixed")
            }
        )
        
        result["request_id"] = request_id
        return result
    
    except Exception as e:
        logger.error(
            f"[{request_id}] Correction failed",
            extra={"error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise CorrectionError(
            f"Failed to correct violations: {str(e)}",
            details={"request_id": request_id, "error_type": type(e).__name__}
        )


@router.post("/suggest", response_model=SuggestionResponse, status_code=200)
async def suggest_improvements(request: Request, suggestion_req: SuggestionRequest):
    """
    Get improvement suggestions for an API specification.
    
    This endpoint:
    1. Analyzes the API specification
    2. Retrieves best practices from vector DB
    3. Uses LLM to generate improvement suggestions
    4. Returns actionable recommendations
    
    **Returns:**
    - List of suggestions with priority
    - Best practice recommendations
    - Security improvements
    - Performance optimizations
    """
    request_id = f"sug_{uuid.uuid4().hex[:8]}"
    
    logger.info(
        f"[{request_id}] Received suggestion request",
        extra={"format": suggestion_req.spec_format}
    )
    
    try:
        corrector_service = get_corrector_service()
        result = await corrector_service.suggest_improvements(
            spec_content=suggestion_req.spec_content,
            spec_format=suggestion_req.spec_format,
            request_id=request_id
        )
        
        logger.info(
            f"[{request_id}] Suggestions generated",
            extra={"total_suggestions": result.get("total_suggestions", 0)}
        )
        
        result["request_id"] = request_id
        return result
    
    except Exception as e:
        logger.error(
            f"[{request_id}] Suggestion generation failed",
            extra={"error": str(e), "error_type": type(e).__name__},
            exc_info=True
        )
        raise ValidationError(
            f"Failed to generate suggestions: {str(e)}",
            details={"request_id": request_id, "error_type": type(e).__name__}
        )


@router.get("/health", status_code=200)
async def health_check():
    """
    Health check for API Governance service.
    
    Returns service status and basic metrics.
    """
    return {
        "status": "healthy",
        "service": "api-governance",
        "version": "1.0.0"
    }
