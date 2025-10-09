# cloud_llm.py
from llm_interface import LLMInterface
from transformers import pipeline
from huggingface_hub import login
from typing import List
import time

class CloudLLM(LLMInterface):
    """
    Cloud LLM using Hugging Face models and API tokens.
    Implements LLMInterface.
    """

    # Default model
    DEFAULT_MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

    def __init__(self, tokens: List[str], model_name: str = None, device: int = -1):
        """
        :param tokens: List of Hugging Face API tokens for rotation
        :param model_name: Hugging Face model repository, default is "meta-llama/Llama-2-7b-chat-hf"
        :param device: Device ID (-1 = CPU, 0 = GPU)
        """
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        self.tokens = tokens or []
        self.device = device
        self.current_token_index = 0
        self.pipe = None
        if self.tokens:
            self._init_pipeline()

    def _login_with_token(self, token: str):
        """Login to Hugging Face hub using a token."""
        login(token=token)

    def _init_pipeline(self):
        """Initialize the Transformers pipeline with the current token."""
        token = self.tokens[self.current_token_index]
        self._login_with_token(token)
        self.pipe = pipeline("text-generation", model=self.model_name, device=self.device)

    def generate(self, prompt: str) -> str:
        return 'hahah'
        """
        Generate text using the cloud Hugging Face model.
        Uses model's default generation parameters.

        :param prompt: Input prompt
        :return: Generated text
        """
        if not self.tokens:
            raise ValueError("No Hugging Face API tokens provided.")

        for _ in range(len(self.tokens)):
            try:
                result = self.pipe(prompt)
                return result[0]['generated_text']
            except Exception as e:
                print(f"[Token {self.current_token_index} failed]: {e}")
                self.current_token_index = (self.current_token_index + 1) % len(self.tokens)
                self._init_pipeline()
                time.sleep(1)

        raise Exception("All tokens failed")
