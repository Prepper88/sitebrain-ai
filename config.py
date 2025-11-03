import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Read configuration values
AZURE_ENDPOINT = os.getenv("AZURE_LLM_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "DeepSeek-R1")
AZURE_DOC_LLM_ENDPOINT = os.getenv("AZURE_DOC_LLM_ENDPOINT")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Validate
if not AZURE_API_KEY or not AZURE_ENDPOINT or not AZURE_DOC_LLM_ENDPOINT:
    raise ValueError("Missing Azure configuration. Please set AZURE_LLM_ENDPOINT, AZURE_API_KEY, AZURE_DOC_LLM_ENDPOINT in the .env file.")

def print_config():
    """Helper for debugging: prints endpoint and model only."""
    print(f"Loaded configuration: endpoint={AZURE_ENDPOINT}, model={LLM_MODEL_NAME}")
