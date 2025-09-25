import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

endpoint = ""
key = ""
deployment_name = "DeepSeek-R1"
command="How many languages are in the world?"

def call_ai(command):
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key),
        api_version="2024-05-01-preview"  # add version of API
    )

    response = client.complete(
        messages=[
            UserMessage(content=command),
        ],
        model="DeepSeek-R1"
    )

    print(response.choices[0].message.content)
    return response.choices[0].message.content