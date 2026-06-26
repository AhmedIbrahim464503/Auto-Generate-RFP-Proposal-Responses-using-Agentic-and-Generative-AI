from typing import Any, Dict, Optional
from backend.app.core.logger import logger

class BaseModelAdapter:
    def __init__(self, model_name: str, config: Dict[str, Any]):
        self.model_name = model_name
        self.config = config

    def generate(self, prompt: str, schema: Any = None) -> Any:
        raise NotImplementedError("Adapters must implement generate")

class GeminiAdapter(BaseModelAdapter):
    def generate(self, prompt: str, schema: Any = None) -> Any:
        logger.info(f"GeminiAdapter: Generating content via model: {self.model_name}")
        return "mock_gemini_response"

class OpenAIAdapter(BaseModelAdapter):
    def generate(self, prompt: str, schema: Any = None) -> Any:
        logger.info(f"OpenAIAdapter: Generating content via model: {self.model_name}")
        return "mock_openai_response"

class ClaudeAdapter(BaseModelAdapter):
    def generate(self, prompt: str, schema: Any = None) -> Any:
        logger.info(f"ClaudeAdapter: Generating content via model: {self.model_name}")
        return "mock_claude_response"

class OllamaAdapter(BaseModelAdapter):
    def generate(self, prompt: str, schema: Any = None) -> Any:
        logger.info(f"OllamaAdapter: Generating content via local Ollama: {self.model_name}")
        return "mock_ollama_response"

class VLLMAdapter(BaseModelAdapter):
    def generate(self, prompt: str, schema: Any = None) -> Any:
        logger.info(f"VLLMAdapter: Generating content via local vLLM: {self.model_name}")
        return "mock_vllm_response"

class ModelAdapterFactory:
    @staticmethod
    def get_adapter(provider: str, model_name: str, config: Dict[str, Any]) -> BaseModelAdapter:
        provider_lower = provider.lower()
        if provider_lower == "gemini":
            return GeminiAdapter(model_name, config)
        elif provider_lower == "openai":
            return OpenAIAdapter(model_name, config)
        elif provider_lower == "claude":
            return ClaudeAdapter(model_name, config)
        elif provider_lower == "ollama":
            return OllamaAdapter(model_name, config)
        elif provider_lower == "vllm":
            return VLLMAdapter(model_name, config)
        else:
            raise ValueError(f"Unknown model provider: {provider}")
