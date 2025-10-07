"""LLM Handler for local inference using llama.cpp.

Provides a simple interface for loading and querying the local Mistral model
for intelligent extraction and categorization tasks.
"""
from pathlib import Path
from typing import Optional, Dict, Any
import json

# Lazy import - will check availability at runtime
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    Llama = None


class LLMHandler:
    """Handler for local LLM inference using llama.cpp.
    
    This is the core AI engine for the Finance AI Dashboard.
    """
    
    def __init__(self, model_path: Optional[Path] = None, n_ctx: int = 4096, n_threads: int = 4):
        """Initialize the LLM handler.
        
        Args:
            model_path: Path to the GGUF model file. Defaults to mistral model in project root.
            n_ctx: Context window size (default 4096).
            n_threads: Number of CPU threads to use (default 4).
        """
        if not LLAMA_CPP_AVAILABLE:
            raise ImportError(
                "\n" + "="*60 + "\n"
                "❌ llama-cpp-python is NOT installed!\n"
                "\n"
                "This Finance AI Dashboard requires LLM capabilities.\n"
                "\n"
                "Install with:\n"
                "  macOS (Apple Silicon):\n"
                "    CMAKE_ARGS=\"-DLLAMA_METAL=on\" pip install llama-cpp-python\n"
                "\n"
                "  Other systems:\n"
                "    pip install llama-cpp-python\n"
                "\n"
                "Or run the setup script:\n"
                "  ./setup.sh\n"
                + "="*60
            )
        
        if model_path is None:
            model_path = Path(__file__).parent / "mistral-7b-instruct-v0.1.Q5_0.gguf"
        
        if not model_path.exists():
            raise FileNotFoundError(
                "\n" + "="*60 + "\n"
                f"❌ Model file not found: {model_path.name}\n"
                "\n"
                "Download the Mistral-7B model (~4.2GB):\n"
                "\n"
                "  wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf\n"
                "\n"
                "Or:\n"
                "  curl -L -o mistral-7b-instruct-v0.1.Q5_0.gguf \\\n"
                "    https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q5_0.gguf\n"
                "\n"
                "Expected location: " + str(model_path) + "\n"
                + "="*60
            )
        
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self.llm: Optional[Llama] = None
        
        # Auto-load model on initialization (AI-first approach)
        print(f"🤖 Initializing AI engine with {model_path.name}...")
        self.load()
        
    def load(self):
        """Load the model into memory."""
        if self.llm is None:
            print(f"Loading LLM from {self.model_path}...")
            self.llm = Llama(
                model_path=str(self.model_path),
                n_ctx=self.n_ctx,
                n_threads=self.n_threads,
                verbose=False
            )
            print("LLM loaded successfully.")
    
    def unload(self):
        """Unload the model from memory."""
        if self.llm is not None:
            del self.llm
            self.llm = None
            print("LLM unloaded.")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1,
        stop: Optional[list] = None
    ) -> str:
        """Generate text from a prompt.
        
        Args:
            prompt: Input prompt for the model.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature (lower = more deterministic).
            stop: List of stop sequences.
            
        Returns:
            str: Generated text.
        """
        if self.llm is None:
            self.load()
        
        response = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            stop=stop or ["</s>", "[INST]", "[/INST]"],
            echo=False
        )
        
        return response['choices'][0]['text'].strip()
    
    def generate_json(
        self,
        prompt: str,
        max_tokens: int = 2048,
        temperature: float = 0.1
    ) -> Dict[Any, Any]:
        """Generate and parse JSON output from a prompt.
        
        Args:
            prompt: Input prompt requesting JSON output.
            max_tokens: Maximum tokens to generate.
            temperature: Sampling temperature.
            
        Returns:
            dict: Parsed JSON response.
        """
        # Add JSON formatting instructions to prompt
        json_prompt = f"""{prompt}

You must respond with valid JSON only. Do not include any explanation or text outside the JSON object."""
        
        response_text = self.generate(json_prompt, max_tokens, temperature)
        
        # Try to extract JSON from response
        try:
            # Find JSON object in response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Try to parse entire response
                return json.loads(response_text)
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from LLM response: {e}")
            print(f"Response was: {response_text}")
            return {"error": "Failed to parse JSON", "raw_response": response_text}
    
    def create_instruct_prompt(self, instruction: str, context: str = "") -> str:
        """Create a Mistral-style instruction prompt.
        
        Args:
            instruction: The instruction/question for the model.
            context: Optional context/data for the instruction.
            
        Returns:
            str: Formatted prompt for Mistral Instruct model.
        """
        if context:
            return f"[INST] {instruction}\n\nContext:\n{context} [/INST]"
        else:
            return f"[INST] {instruction} [/INST]"


# Global singleton instance
_llm_handler: Optional[LLMHandler] = None


def get_llm_handler() -> LLMHandler:
    """Get or create the global LLM handler instance.
    
    Returns:
        LLMHandler: The global LLM handler.
    """
    global _llm_handler
    if _llm_handler is None:
        _llm_handler = LLMHandler()
    return _llm_handler


def is_llm_available() -> bool:
    """Check if LLM dependencies are available.
    
    Returns:
        bool: True if llama-cpp-python is installed.
    """
    return LLAMA_CPP_AVAILABLE
