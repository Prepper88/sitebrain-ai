from llm_interface import LLMInterface
import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage
import time
import re
import config

endpoint = config.AZURE_ENDPOINT
key = config.AZURE_API_KEY
deployment_name = config.LLM_MODEL_NAME
command="How many languages are in the world?"

class CloudLLM(LLMInterface):
    """
    Cloud LLM using Azure OpenAI models and API tokens.
    Implements LLMInterface.
    """

    # Default model
    DEFAULT_MODEL_NAME = "DeepSeek-R1"

    def __init__(self, model_name: str = None, remove_think_tags: bool = False):
        """
        Initialize CloudLLM
        :param model_name: Azure OpenAI model name, default is "DeepSeek-R1"
        """
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        self.remove_think_tags = remove_think_tags

    def generate(self, prompt: str) -> str:
        """
        Generate text using the cloud Azure OpenAI model.
        Uses model's default generation parameters.

        :param prompt: Input prompt
        :return: Generated text
        """
        client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            api_version="2024-05-01-preview"  # add version of API
        )

        response = client.complete(
            messages=[
                UserMessage(content=prompt),
            ],
            model="DeepSeek-R1"
        )

        print(response.choices[0].message.content)
        if remove_think_tags:
            return remove_think_tags(response.choices[0].message.content)
        return response.choices[0].message.content

def remove_think_tags(text: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
   
if __name__ == '__main__':
    llm_interface = CloudLLM()
    response = llm_interface.generate("How many languages are in the world?")
    print(response)