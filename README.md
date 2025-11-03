# sitebrain-ai
## Local Model
``` shell
# install ollama
brew install ollama
# run ollama daemon
nohup ollama serve > ollama.log 2>&1 &
# pull LLAMA2
ollama pull llama2
# run LLAMA2
ollama run llama2
```
## Cloud Model
### appkey application
* signup account
* create read token
https://huggingface.co/settings/tokens 
* apply model
https://huggingface.co/meta-llama/Llama-2-7b-chat-hf

## Sample Questions
* What’s the maximum hot-water temperature allowed by code?