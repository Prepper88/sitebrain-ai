from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage

# Azure configuration
endpoint = "your_endpoint"
key = "your_api_key"
deployment_name = "DeepSeek-R1"

# Create client
client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key),
    api_version="2024-05-01-preview"
)

print("=== AI Chat (type 'exit' to quit) ===")

# Loop for chat
while True:
    command = input("You: ")
    if command.lower() in ["exit", "quit"]:
        print("Chat ended. Goodbye!")
        break

    response = client.complete(
        messages=[UserMessage(content=command)],
        model=deployment_name
    )

    reply = response.choices[0].message.content
    print("AI:", reply)
