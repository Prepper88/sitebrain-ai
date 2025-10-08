from local_llm_ollama import LocalLLM
from cloud_llm import CloudLLM

# 本地模型
#local_model = LocalLLM()
#print(local_model.generate("请用中文介绍 LLaMA 2 模型"))

# 云端模型
cloud_model = CloudLLM(tokens=["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"])
#print(cloud_model.generate("请用中文解释 RAG 模型"))
