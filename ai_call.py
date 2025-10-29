import os
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import SystemMessage, UserMessage

endpoint = "https://chen9m1-deepseek-r1.services.ai.azure.com/models"
key = "8Z7g2A07b2ItypQ2JOhMTwzQiKCcC4t657j3mWeqhMUtL4ZLYgcWJQQJ99BIACHYHv6XJ3w3AAAAACOGtDyz"
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
if __name__ == '__main__':
    call_ai(command)