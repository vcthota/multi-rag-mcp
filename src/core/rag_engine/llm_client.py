"""
Core RAG Engine - LLM Client
Handles interaction with OpenAI API
"""
from typing import List, Optional, Dict, Any
from openai import AsyncOpenAI
import logging

from src.config.settings import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMClient:
    """LLM client for OpenAI API"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
    
    async def generate(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion from prompt"""
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate JSON response"""
        import json
        
        if not system_message:
            system_message = "You are a helpful assistant that responds in JSON format."
        
        response = await self.generate(
            prompt=prompt,
            system_message=system_message,
            response_format={"type": "json_object"},
            **kwargs
        )
        
        return json.loads(response)
    
    async def generate_with_context(
        self,
        query: str,
        context: List[str],
        system_message: Optional[str] = None,
        **kwargs
    ) -> str:
        """Generate response with retrieved context"""
        
        # Build prompt with context
        context_str = "\n\n".join([f"Context {i+1}:\n{ctx}" for i, ctx in enumerate(context)])
        
        prompt = f"""Based on the following context, answer the query.

{context_str}

Query: {query}

Answer:"""
        
        return await self.generate(
            prompt=prompt,
            system_message=system_message,
            **kwargs
        )


# Singleton instance
_llm_client = None

def get_llm_client() -> LLMClient:
    """Get LLM client instance"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
