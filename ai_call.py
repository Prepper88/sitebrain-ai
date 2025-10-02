from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.ai.inference.models import UserMessage, SystemMessage, AssistantMessage

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

print("=== AI Chat with Memory (type 'exit' to quit) ===")

# Initialize conversation memory
messages = [
    SystemMessage(content="You are a helpful AI assistant.")
]

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Chat ended. Goodbye!")
        break

    # Add user message to memory
    messages.append(UserMessage(content=user_input))

    # Call the AI model
    response = client.complete(
        messages=messages,
        model=deployment_name
    )

    reply = response.choices[0].message.content
    print("AI:", reply)

    # Add AI response to memory
    messages.append(AssistantMessage(content=reply))
