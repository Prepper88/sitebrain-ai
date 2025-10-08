# llm_interface.py
from abc import ABC, abstractmethod

class LLMInterface(ABC):
    """
    Abstract base class for all LLMs.
    Defines a common interface for local or cloud LLMs.
    """

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """
        Generate text from a given prompt.
        
        :param prompt: Input prompt string
        :param max_tokens: Maximum number of tokens to generate (default: 100)
        :return: Generated text string
        """
        pass
