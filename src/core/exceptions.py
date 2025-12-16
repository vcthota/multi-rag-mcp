"""
Custom exceptions for the Multi-RAG platform
"""
from typing import Any, Optional, Dict


class MultiRAGException(Exception):
    """Base exception for all Multi-RAG errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


# API Governance Exceptions
class GovernanceException(MultiRAGException):
    """Base exception for API Governance service"""
    pass


class PDFProcessingError(GovernanceException):
    """Error processing PDF document"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="PDF_PROCESSING_ERROR",
            status_code=400,
            details=details
        )


class InvalidSpecificationError(GovernanceException):
    """Invalid API specification format"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="INVALID_SPECIFICATION",
            status_code=400,
            details=details
        )


class ValidationError(GovernanceException):
    """Error during validation process"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details
        )


class CorrectionError(GovernanceException):
    """Error during correction process"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CORRECTION_ERROR",
            status_code=500,
            details=details
        )


# Vector Store Exceptions
class VectorStoreException(MultiRAGException):
    """Base exception for vector store operations"""
    pass


class EmbeddingError(VectorStoreException):
    """Error generating embeddings"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="EMBEDDING_ERROR",
            status_code=500,
            details=details
        )


class VectorSearchError(VectorStoreException):
    """Error searching vector store"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VECTOR_SEARCH_ERROR",
            status_code=500,
            details=details
        )


# LLM Exceptions
class LLMException(MultiRAGException):
    """Base exception for LLM operations"""
    pass


class LLMRateLimitError(LLMException):
    """LLM rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


class LLMTimeoutError(LLMException):
    """LLM request timeout"""
    
    def __init__(self, message: str = "LLM request timeout", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="LLM_TIMEOUT",
            status_code=504,
            details=details
        )


class LLMAPIError(LLMException):
    """LLM API error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="LLM_API_ERROR",
            status_code=502,
            details=details
        )


# File Processing Exceptions
class FileProcessingException(MultiRAGException):
    """Base exception for file processing"""
    pass


class FileSizeExceededError(FileProcessingException):
    """File size exceeds limit"""
    
    def __init__(self, max_size: int, actual_size: int):
        super().__init__(
            message=f"File size {actual_size} bytes exceeds maximum allowed size of {max_size} bytes",
            error_code="FILE_SIZE_EXCEEDED",
            status_code=413,
            details={"max_size": max_size, "actual_size": actual_size}
        )


class UnsupportedFileTypeError(FileProcessingException):
    """Unsupported file type"""
    
    def __init__(self, file_type: str, supported_types: list):
        super().__init__(
            message=f"File type '{file_type}' is not supported. Supported types: {', '.join(supported_types)}",
            error_code="UNSUPPORTED_FILE_TYPE",
            status_code=415,
            details={"file_type": file_type, "supported_types": supported_types}
        )


# Configuration Exceptions
class ConfigurationError(MultiRAGException):
    """Configuration error"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details
        )
