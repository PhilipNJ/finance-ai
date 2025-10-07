"""Ollama-based multi-model LLM handler.

Provides a simple interface for querying local models via the Ollama REST API,
and supports different models per agent type (extraction, organizer, database).

This module intentionally avoids importing llama-cpp to keep the project light
and to use the faster Ollama runtime instead.
"""
from typing import Optional, Dict, Any
import os
import json
import requests


# Agent type strings
AgentType = str  # one of: "extraction", "organizer", "database"


class MultiModelLLMHandler:
    """LLM handler using Ollama REST API with per-agent models."""

    DEFAULT_MODELS: Dict[str, str] = {
        # Recommended balanced defaults
        "extraction": "phi3.5:3.8b-mini-instruct-q4_K_M",
        "organizer": "gemma2:2b-instruct-q4_K_M",
        "database": "codellama:7b-instruct-q4_K_M",
    }

    def __init__(self, api_url: Optional[str] = None, custom_models: Optional[Dict[str, str]] = None) -> None:
        self.api_url = api_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.models = custom_models or self.DEFAULT_MODELS

    # Backwards-compatible method expected by agents.py
    def create_instruct_prompt(self, instruction: str, context: str = "") -> str:
        """Create a generic instruction prompt (model-agnostic)."""
        if context:
            return f"Instruction: {instruction}\n\nContext:\n{context}"
        return f"Instruction: {instruction}"

    def generate_json(
        self,
        prompt: str,
        max_tokens: int = 256,
        temperature: float = 0.1,
        agent_type: AgentType = "extraction",
    ) -> Dict[str, Any]:
        """Generate and parse JSON output using Ollama (format=json)."""
        text = self._ollama_generate(prompt, self.models[agent_type], max_tokens, temperature, json_mode=True)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract JSON block
            start_idx = text.find("{")
            end_idx = text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                try:
                    return json.loads(text[start_idx:end_idx])
                except Exception:
                    pass
            return {"error": "Failed to parse JSON", "raw_response": text}

    # Internal: call Ollama REST API
    def _ollama_generate(self, prompt: str, model: str, max_tokens: int, temperature: float, json_mode: bool = False) -> str:
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
            },
        }
        if json_mode:
            payload["format"] = "json"

        resp = requests.post(f"{self.api_url}/api/generate", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return (data.get("response") or "").strip()


# Global singleton
_llm_handler: Optional[MultiModelLLMHandler] = None


def get_llm_handler() -> MultiModelLLMHandler:
    global _llm_handler
    if _llm_handler is None:
        # Allow model overrides via env
        custom: Optional[Dict[str, str]] = None
        if os.getenv("LLM_EXTRACTION_MODEL"):
            custom = {
                "extraction": os.getenv("LLM_EXTRACTION_MODEL", MultiModelLLMHandler.DEFAULT_MODELS["extraction"]),
                "organizer": os.getenv("LLM_ORGANIZER_MODEL", MultiModelLLMHandler.DEFAULT_MODELS["organizer"]),
                "database": os.getenv("LLM_DATABASE_MODEL", MultiModelLLMHandler.DEFAULT_MODELS["database"]),
            }
        _llm_handler = MultiModelLLMHandler(api_url=os.getenv("OLLAMA_URL"), custom_models=custom)
    return _llm_handler


def is_llm_available() -> bool:
    """Check if Ollama API is reachable."""
    try:
        url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        resp = requests.get(f"{url}/api/tags", timeout=2)
        return resp.ok
    except Exception:
        return False
