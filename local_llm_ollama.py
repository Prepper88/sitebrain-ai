# local_llm_ollama.py
from llm_interface import LLMInterface
import subprocess

class LocalLLM(LLMInterface):
    """
    Local LLM using Ollama CLI to generate text.
    Implements LLMInterface.
    """

    # Default model
    DEFAULT_MODEL_NAME = "llama2"

    def __init__(self, model_name: str = None):
        """
        :param model_name: Local Ollama model name, default is "llama2"
        """
        self.model_name = model_name or self.DEFAULT_MODEL_NAME

    def generate(self, prompt: str) -> str:
        """
        Generate text using local Ollama model via CLI.
        Uses model's default generation parameters.

        :param prompt: Input prompt
        :return: Generated text
        """
        cmd = [
            "ollama", "run", self.model_name, prompt
        ]

        print(f"Running command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise Exception(f"Ollama CLI call failed: {e.stderr}")
