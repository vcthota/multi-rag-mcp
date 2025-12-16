"""
API Governance Service - REST API Router
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import os

from src.services.api_governance.ingestion import get_ingestion_service
from src.services.api_governance.validator import get_validator_service
from src.services.api_governance.corrector import get_corrector_service

router = APIRouter()


# Request/Response Models
class ValidateRequest(BaseModel):
    """Validation request"""
    spec_content: str = Field(..., description="API specification content")
    spec_format: str = Field(default="json", description="Specification format (json/yaml)")


class ValidateResponse(BaseModel):
    """Validation response"""
    valid: bool
    compliance_score: float
    violations: List[Dict[str, Any]]
    rules_checked: int
    features_analyzed: int


class CorrectRequest(BaseModel):
    """Correction request"""
    spec_content: str = Field(..., description="API specification content")
    violations: List[Dict[str, Any]] = Field(..., description="Violations to correct")
    spec_format: str = Field(default="json", description="Specification format (json/yaml)")


class CorrectResponse(BaseModel):
    """Correction response"""
    corrected: bool
    corrected_spec: str
    changes: List[Dict[str, Any]]
    violations_fixed: int


class IngestionResponse(BaseModel):
    """Ingestion response"""
    success: bool
    document: str
    chunks_created: int
    ids: List[str]


# Endpoints
@router.post("/ingest", response_model=IngestionResponse)
async def ingest_governance_document(
    file: UploadFile = File(..., description="PDF document containing governance rules")
):
    """
    Ingest a governance document (PDF) into the vector database.
    
    This endpoint:
    1. Extracts text from the PDF
    2. Splits into chunks
    3. Generates embeddings
    4. Stores in vector database
    """
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        ingestion = get_ingestion_service()
        result = await ingestion.ingest_pdf(
            pdf_path=tmp_path,
            metadata={"filename": file.filename}
        )
        
        return IngestionResponse(**result)
    
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.post("/validate", response_model=ValidateResponse)
async def validate_api_spec(request: ValidateRequest):
    """
    Validate an API specification against governance rules.
    
    This endpoint:
    1. Parses the API specification
    2. Extracts features
    3. Retrieves relevant governance rules
    4. Checks for violations
    5. Returns compliance score and violations
    """
    
    try:
        validator = get_validator_service()
        result = await validator.validate_spec(
            spec_content=request.spec_content,
            spec_format=request.spec_format
        )
        
        return ValidateResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation error: {str(e)}")


@router.post("/correct", response_model=CorrectResponse)
async def correct_api_spec(request: CorrectRequest):
    """
    Automatically correct violations in an API specification.
    
    This endpoint:
    1. Takes the spec and violations
    2. Uses LLM to generate corrections
    3. Returns corrected specification with changes
    """
    
    try:
        corrector = get_corrector_service()
        result = await corrector.correct_violations(
            spec_content=request.spec_content,
            violations=request.violations,
            spec_format=request.spec_format
        )
        
        return CorrectResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Correction error: {str(e)}")


@router.post("/suggest")
async def suggest_improvements(
    spec_content: str = Form(...),
    spec_format: str = Form(default="json")
):
    """
    Get improvement suggestions for an API specification.
    
    This endpoint provides suggestions beyond compliance:
    - Security best practices
    - Documentation improvements
    - Error handling patterns
    - Performance considerations
    """
    
    try:
        corrector = get_corrector_service()
        suggestions = await corrector.suggest_improvements(
            spec_content=spec_content,
            spec_format=spec_format
        )
        
        return {"suggestions": suggestions}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Suggestion error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "api-governance"}
