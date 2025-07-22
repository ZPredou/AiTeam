#!/usr/bin/env python3
"""
AI Providers - Integration with real AI APIs for agent responses

Supports multiple AI providers:
- OpenAI GPT-4/GPT-3.5
- Anthropic Claude
- Google Gemini
- Local models via Ollama
- Azure OpenAI
"""

import json
import asyncio
import aiohttp
import os
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

class AIProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    OLLAMA = "ollama"
    AZURE_OPENAI = "azure_openai"

@dataclass
class AIResponse:
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

class BaseAIProvider(ABC):
    """Base class for AI providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response from AI provider"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name being used"""
        pass

class OpenAIProvider(BaseAIProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
    
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using OpenAI API"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1000),
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        # Create SSL context that's more permissive
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        connector = aiohttp.TCPConnector(ssl=ssl_context)

        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens")
                
                return AIResponse(
                    content=content,
                    provider="openai",
                    model=self.model,
                    tokens_used=tokens_used,
                    cost_estimate=self._estimate_cost(tokens_used)
                )
    
    def get_model_name(self) -> str:
        return self.model
    
    def _estimate_cost(self, tokens: Optional[int]) -> Optional[float]:
        """Estimate cost based on tokens (rough estimates)"""
        if not tokens:
            return None
        
        # Rough cost estimates per 1K tokens (as of 2024)
        costs = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.002
        }
        
        cost_per_1k = costs.get(self.model, 0.01)
        return (tokens / 1000) * cost_per_1k

class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("Anthropic API key required. Set ANTHROPIC_API_KEY environment variable.")
    
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Anthropic API"""
        
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": self.model,
            "max_tokens": kwargs.get("max_tokens", 1000),
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API error: {response.status} - {error_text}")
                
                data = await response.json()
                content = data["content"][0]["text"]
                
                return AIResponse(
                    content=content,
                    provider="anthropic",
                    model=self.model,
                    tokens_used=data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                )
    
    def get_model_name(self) -> str:
        return self.model

class OllamaProvider(BaseAIProvider):
    """Local Ollama provider"""
    
    def __init__(self, model: str = "llama2", base_url: str = "http://localhost:11434", **kwargs):
        super().__init__(**kwargs)
        self.model = model
        self.base_url = base_url
    
    async def generate_response(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Ollama API"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json=payload
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Ollama API error: {response.status} - {error_text}")
                
                data = await response.json()
                
                return AIResponse(
                    content=data["response"],
                    provider="ollama",
                    model=self.model
                )
    
    def get_model_name(self) -> str:
        return self.model

class AIProviderManager:
    """Manages different AI providers and handles failover"""
    
    def __init__(self, primary_provider: AIProvider = AIProvider.OPENAI, **provider_configs):
        self.primary_provider = primary_provider
        self.provider_configs = provider_configs
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers"""
        
        # OpenAI
        if self.primary_provider == AIProvider.OPENAI or "openai" in self.provider_configs:
            try:
                config = self.provider_configs.get("openai", {})
                self.providers[AIProvider.OPENAI] = OpenAIProvider(**config)
            except Exception as e:
                print(f"⚠️  OpenAI provider not available: {e}")
        
        # Anthropic
        if self.primary_provider == AIProvider.ANTHROPIC or "anthropic" in self.provider_configs:
            try:
                config = self.provider_configs.get("anthropic", {})
                self.providers[AIProvider.ANTHROPIC] = AnthropicProvider(**config)
            except Exception as e:
                print(f"⚠️  Anthropic provider not available: {e}")
        
        # Ollama (local)
        if self.primary_provider == AIProvider.OLLAMA or "ollama" in self.provider_configs:
            try:
                config = self.provider_configs.get("ollama", {})
                self.providers[AIProvider.OLLAMA] = OllamaProvider(**config)
            except Exception as e:
                print(f"⚠️  Ollama provider not available: {e}")
        
        if not self.providers:
            print("⚠️  No AI providers available! Using mock responses.")
    
    async def generate_response(self, prompt: str, agent_role: str = "assistant", **kwargs) -> AIResponse:
        """Generate response with failover support"""
        
        # Try primary provider first
        if self.primary_provider in self.providers:
            try:
                return await self.providers[self.primary_provider].generate_response(prompt, **kwargs)
            except Exception as e:
                print(f"⚠️  Primary provider ({self.primary_provider.value}) failed: {e}")
        
        # Try other providers as fallback
        for provider_type, provider in self.providers.items():
            if provider_type != self.primary_provider:
                try:
                    print(f"🔄 Trying fallback provider: {provider_type.value}")
                    return await provider.generate_response(prompt, **kwargs)
                except Exception as e:
                    print(f"⚠️  Fallback provider ({provider_type.value}) failed: {e}")
        
        # If all providers fail, raise an exception so the calling code can handle it
        print("⚠️  All AI providers failed. Letting caller handle fallback.")
        raise Exception("All AI providers failed - use intelligent fallback")
    
    def get_available_providers(self) -> list[str]:
        """Get list of available providers"""
        return [provider.value for provider in self.providers.keys()]
    
    def set_primary_provider(self, provider: AIProvider):
        """Change the primary provider"""
        if provider in self.providers:
            self.primary_provider = provider
            print(f"🔄 Primary provider changed to: {provider.value}")
        else:
            print(f"❌ Provider {provider.value} not available")

# Helper function to create provider manager with configuration
def create_ai_provider_manager() -> AIProviderManager:
    """Create AI provider manager with automatic configuration"""

    # Load configuration from file
    config_path = "ai_config.json"
    provider_configs = {}
    primary_provider = AIProvider.OPENAI  # Default

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)

        ai_config = config.get("ai_providers", {})
        primary_provider_name = ai_config.get("primary_provider", "openai")

        # Configure OpenAI from config file
        openai_config = ai_config.get("providers", {}).get("openai", {})
        if openai_config.get("api_key"):
            provider_configs["openai"] = {
                "model": openai_config.get("model", "gpt-3.5-turbo"),
                "api_key": openai_config["api_key"]
            }
            primary_provider = AIProvider.OPENAI
            print(f"✅ OpenAI configured with model: {openai_config.get('model', 'gpt-3.5-turbo')}")

    except FileNotFoundError:
        print("⚠️  ai_config.json not found, checking environment variables...")

    # Fallback to environment variables if config file doesn't work
    if not provider_configs.get("openai"):
        if os.getenv("OPENAI_API_KEY"):
            provider_configs["openai"] = {
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                "api_key": os.getenv("OPENAI_API_KEY")
            }
            primary_provider = AIProvider.OPENAI
    
    # Anthropic
    if os.getenv("ANTHROPIC_API_KEY"):
        provider_configs["anthropic"] = {
            "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            "api_key": os.getenv("ANTHROPIC_API_KEY")
        }
        if not provider_configs.get("openai"):  # Use as primary if OpenAI not available
            primary_provider = AIProvider.ANTHROPIC
    
    # Ollama (always try local)
    provider_configs["ollama"] = {
        "model": os.getenv("OLLAMA_MODEL", "llama2"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    }
    
    # If we have OpenAI configured from config file, use it as primary
    if provider_configs.get("openai"):
        primary_provider = AIProvider.OPENAI
        print("🎯 Using OpenAI as primary provider (configured in ai_config.json)")
    # If no API keys found, use Ollama as primary
    elif not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        primary_provider = AIProvider.OLLAMA
        print("💡 No API keys found. Using local Ollama as primary provider.")
        print("   Make sure Ollama is running: ollama serve")
    
    return AIProviderManager(primary_provider, **provider_configs)

# Example usage and testing
async def test_providers():
    """Test different AI providers"""
    
    manager = create_ai_provider_manager()
    
    print(f"🤖 Available providers: {', '.join(manager.get_available_providers())}")
    print(f"🎯 Primary provider: {manager.primary_provider.value}")
    
    test_prompt = """You are a senior software engineer. Analyze this task:

Task: Implement user authentication system
Description: Create secure login with JWT tokens

Provide a brief technical analysis including:
1. Approach
2. Key considerations
3. Estimated effort

Keep response under 200 words."""
    
    try:
        response = await manager.generate_response(test_prompt)
        print(f"\n✅ Response from {response.provider} ({response.model}):")
        print(f"📝 {response.content[:200]}...")
        if response.tokens_used:
            print(f"🔢 Tokens used: {response.tokens_used}")
        if response.cost_estimate:
            print(f"💰 Estimated cost: ${response.cost_estimate:.4f}")
    
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_providers())
