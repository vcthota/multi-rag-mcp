"""
Script to run API Governance PDF ingestion pipeline
"""
import asyncio
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Run the ingestion pipeline"""
    
    # PDF file path
    pdf_path = "/Users/venkatathota/AI-Courses/projects/multi-rag-mcp/src/services/api_governance/pdfs/Enterprise Rest Api Design & Governance Guide.pdf"
    
    # Check if file exists
    if not Path(pdf_path).exists():
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)
    
    logger.info(f"Starting ingestion for: {pdf_path}")
    
    try:
        # Import the ingestion service
        from src.services.api_governance.ingestion import get_ingestion_service
        
        # Create ingestion service
        ingestion_service = get_ingestion_service()
        
        # Ingest the PDF
        result = await ingestion_service.ingest_pdf(
            pdf_path=pdf_path,
            metadata={
                "document_type": "Enterprise API Governance Guide",
                "version": "1.0",
                "category": "governance_standards"
            }
        )
        
        # Print results
        logger.info("=" * 80)
        logger.info("INGESTION COMPLETED SUCCESSFULLY")
        logger.info("=" * 80)
        logger.info(f"Document: {result['document']}")
        logger.info(f"Chunks Created: {result['chunks_created']}")
        logger.info(f"Success: {result['success']}")
        logger.info(f"Sample IDs: {result['ids'][:3]}...")
        logger.info("=" * 80)
        
        return result
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
