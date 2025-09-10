from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio
import logging
from anthropic import Anthropic
from openai import OpenAI
from src.config import settings

logger = logging.getLogger(__name__)


class BaseLLMService(ABC):
    """Abstract base class for LLM services"""
    
    @abstractmethod
    async def generate_text(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate text from messages"""
        pass
    
    @abstractmethod
    async def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        pass


class AnthropicService(BaseLLMService):
    """Anthropic Claude service integration"""
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate_text(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "claude-3-sonnet-20240229",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using Claude"""
        try:
            # Convert messages to Claude format
            system_message = ""
            user_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    user_messages.append(msg)
            
            response = await asyncio.to_thread(
                self.client.messages.create,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_message,
                messages=user_messages,
                **kwargs
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Failed to generate text with Claude: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        """Estimate token count for Claude (approximate)"""
        # Claude uses a similar tokenization to GPT-3.5/4
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4


class OpenAIService(BaseLLMService):
    """OpenAI service integration"""
    
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate_text(
        self, 
        messages: List[Dict[str, str]], 
        model: str = "gpt-4",
        max_tokens: int = 4000,
        temperature: float = 0.7,
        **kwargs
    ) -> str:
        """Generate text using OpenAI GPT"""
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"Failed to generate text with OpenAI: {str(e)}")
    
    async def count_tokens(self, text: str) -> int:
        """Estimate token count for OpenAI models"""
        try:
            # Use tiktoken for accurate count if available
            import tiktoken
            encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to rough estimation
            return len(text) // 4


class LLMServiceFactory:
    """Factory for creating LLM service instances"""
    
    _instances = {}
    
    @classmethod
    def get_service(cls, provider: str) -> BaseLLMService:
        """Get LLM service instance"""
        if provider not in cls._instances:
            if provider.lower() in ["claude", "anthropic"]:
                cls._instances[provider] = AnthropicService()
            elif provider.lower() in ["openai", "gpt-4", "gpt-3.5"]:
                cls._instances[provider] = OpenAIService()
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
        
        return cls._instances[provider]


class LLMOrchestrator:
    """Orchestrator for managing multiple LLM services"""
    
    def __init__(self):
        self.services = {}
        
        # Initialize available services
        if settings.ANTHROPIC_API_KEY:
            try:
                self.services["claude"] = AnthropicService()
            except Exception as e:
                logger.warning(f"Failed to initialize Anthropic service: {e}")
        
        if settings.OPENAI_API_KEY:
            try:
                self.services["openai"] = OpenAIService()
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI service: {e}")
    
    async def generate_with_fallback(
        self, 
        messages: List[Dict[str, str]], 
        preferred_provider: str = "claude",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text with fallback to other providers"""
        
        providers_to_try = [preferred_provider]
        if preferred_provider != "claude" and "claude" in self.services:
            providers_to_try.append("claude")
        if preferred_provider != "openai" and "openai" in self.services:
            providers_to_try.append("openai")
        
        for provider in providers_to_try:
            if provider in self.services:
                try:
                    result = await self.services[provider].generate_text(messages, **kwargs)
                    return {
                        "text": result,
                        "provider": provider,
                        "success": True
                    }
                except Exception as e:
                    logger.warning(f"Provider {provider} failed: {e}")
                    continue
        
        raise Exception("All LLM providers failed")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available LLM providers"""
        return list(self.services.keys())
    
    async def estimate_tokens(self, text: str, provider: str = "claude") -> int:
        """Estimate token count for text"""
        if provider in self.services:
            return await self.services[provider].count_tokens(text)
        else:
            # Fallback estimation
            return len(text) // 4


# Global orchestrator instance
llm_orchestrator = LLMOrchestrator()
