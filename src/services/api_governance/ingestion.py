"""
API Governance Service - PDF Ingestion Pipeline
Extracts governance rules from PDF documents and stores in vector DB
"""
from typing import List, Dict, Any
import logging
from pathlib import Path
import uuid

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.core.rag_engine.embeddings import get_embedding_model
from src.core.rag_engine.vector_store import get_vector_store
from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GovernanceIngestion:
    """PDF ingestion pipeline for API governance documents"""
    
    def __init__(self):
        self.embedding_model = get_embedding_model()
        self.vector_store = get_vector_store(settings.PINECONE_INDEX_API_GOVERNANCE)
        
        # Text splitter configuration
        chunk_size = 1000  # Characters per chunk
        chunk_overlap = 200  # Overlap between chunks
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def ingest_pdf(self, pdf_path: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Ingest PDF document and store in vector DB"""
        
        logger.info(f"Starting PDF ingestion: {pdf_path}")
        
        try:
            # Extract text from PDF
            text = self._extract_text(pdf_path)
            
            if not text.strip():
                raise ValueError("No text extracted from PDF")
            
            # Split into chunks
            chunks = self._split_text(text)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Generate embeddings
            embeddings = await self.embedding_model.embed_batch(chunks)
            
            # Prepare metadata
            base_metadata = metadata or {}
            base_metadata.update({
                "source": Path(pdf_path).name,
                "type": "governance_rule",
                "total_chunks": len(chunks)
            })
            
            # Create IDs and metadata for each chunk
            ids = [str(uuid.uuid4()) for _ in chunks]
            chunk_metadata = [
                {
                    **base_metadata,
                    "chunk_index": i,
                    "text": chunk
                }
                for i, chunk in enumerate(chunks)
            ]
            
            # Upsert to vector DB
            await self.vector_store.upsert(
                ids=ids,
                embeddings=embeddings,
                metadata=chunk_metadata
            )
            
            logger.info(f"Successfully ingested {len(chunks)} chunks from {pdf_path}")
            
            return {
                "success": True,
                "document": Path(pdf_path).name,
                "chunks_created": len(chunks),
                "ids": ids
            }
        
        except Exception as e:
            logger.error(f"Error ingesting PDF: {e}")
            raise
    
    def _extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        
        try:
            reader = PdfReader(pdf_path)
            text_parts = []
            
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"[Page {page_num + 1}]\n{page_text}")
            
            return "\n\n".join(text_parts)
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into chunks"""
        
        chunks = self.text_splitter.split_text(text)
        
        # Filter out very small chunks
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        
        return chunks
    
    async def ingest_directory(self, directory: str) -> List[Dict[str, Any]]:
        """Ingest all PDFs from a directory"""
        
        directory_path = Path(directory)
        pdf_files = list(directory_path.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory}")
        
        results = []
        for pdf_file in pdf_files:
            try:
                result = await self.ingest_pdf(str(pdf_file))
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to ingest {pdf_file}: {e}")
                results.append({
                    "success": False,
                    "document": pdf_file.name,
                    "error": str(e)
                })
        
        return results


def get_ingestion_service() -> GovernanceIngestion:
    """Get ingestion service instance"""
    return GovernanceIngestion()
