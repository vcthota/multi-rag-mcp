"""
Application Configuration
Uses Pydantic Settings for environment variable management
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env file
    )
    
    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-large"
    OPENAI_MAX_TOKENS: int = 4096
    OPENAI_TEMPERATURE: float = 0.3
    
    # Vector Database (Pinecone)
    PINECONE_API_KEY: str = ""
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_API_GOVERNANCE: str = "api-governance-rules"
    PINECONE_INDEX_GRAPHQL: str = "graphql-schemas"
    PINECONE_INDEX_LOG_PATTERNS: str = "log-patterns"
    
    # ChromaDB (Development)
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma"
    
    # PostgreSQL
    DATABASE_URL: str = "postgresql://admin:admin123@localhost:5432/multirag"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_CACHE_TTL: int = 3600
    
    # RAG Engine
    RETRIEVAL_TOP_K: int = 20
    RETRIEVAL_SIMILARITY_THRESHOLD: float = 0.85
    EMBEDDING_BATCH_SIZE: int = 100
    EMBEDDING_DIMENSION: int = 3072
    
    # Security
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Service-specific
    API_GOVERNANCE_MAX_SPEC_SIZE_MB: int = 10
    GRAPHQL_MAX_SCHEMA_SIZE_MB: int = 5
    LOG_CLASSIFIER_SAMPLE_RATE: float = 1.0
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"
    
    @property
    def use_pinecone(self) -> bool:
        """Check if Pinecone should be used"""
        return bool(self.PINECONE_API_KEY)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
