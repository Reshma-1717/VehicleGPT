import os
import logging
from typing import Optional, Dict, Any
from backend.app.core.config import settings

logger = logging.getLogger("vehiclegpt.llm.local_slm")

class LocalSLM:
    """
    Local On-Device SLM Runner using llama.cpp / GGUF quantization.
    Designed for edge profiles (e.g., Llama 3.2 1B Instruct or Qwen 2.5 1.5B Q4_K_M).
    Operates strictly offline without external network dependencies.
    """

    def __init__(self):
        self.model_path = settings.LLM_MODEL_PATH
        self.context_size = settings.LLM_CONTEXT_SIZE
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.llm = None
        self._load_attempted = False
        self._init_model()

    def _init_model(self) -> None:
        if not os.path.exists(self.model_path):
            logger.info(
                f"Local GGUF model not found at '{self.model_path}'. "
                "VehicleGPT will use verified deterministic local fallback templates."
            )
            return

        try:
            from llama_cpp import Llama
            logger.info(f"Loading local SLM weights from {self.model_path} (n_ctx={self.context_size})...")
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.context_size,
                n_threads=2,  # Constrained ARM 2-core budget
                verbose=False
            )
            logger.info("Local SLM initialized successfully.")
        except ImportError:
            logger.info("llama-cpp-python not installed in this environment. Using deterministic fallback.")
        except Exception as e:
            logger.warning(f"Could not initialize local SLM: {e}. Falling back to deterministic engine.")

    def is_available(self) -> bool:
        return self.llm is not None

    def generate_explanation(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        if not self.is_available():
            return None

        try:
            full_prompt = (
                f"<|system|>\n{system_prompt}\n"
                f"<|user|>\n{prompt}\n"
                f"<|assistant|>\n"
            )
            output = self.llm(
                full_prompt,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stop=["<|user|>", "<|system|>", "\n\n\n"]
            )
            return output["choices"][0]["text"].strip()
        except Exception as e:
            logger.error(f"Local SLM inference error: {e}")
            return None

local_slm = LocalSLM()
