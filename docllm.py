import base64
import requests
import os


def document_to_base64(file_path):
    """将文件转换为 base64 字符串"""
    with open(file_path, "rb") as file:
        file_data = file.read()
        base64_encoded = base64.b64encode(file_data).decode('utf-8')
    return base64_encoded


def send_to_mistral_api(file_path, is_pdf=True):
    """发送文档到 Mistral API"""

    # 读取 API 密钥
    api_key = "8Z7g2A07b2ItypQ2JOhMTwzQiKCcC4t657j3mWeqhMUtL4ZLYgcWJQQJ99BIACHYHv6XJ3w3AAAAACOGtDyz"

    # 转换文件为 base64
    base64_content = document_to_base64(file_path)

    # 根据文件类型设置参数
    if is_pdf:
        document_type = "document_url"
        data_url = f"data:application/pdf;base64,{base64_content}"
    else:
        document_type = "image_url"
        data_url = f"data:image/jpeg;base64,{base64_content}"

    # 准备请求数据
    payload = {
        "model": "mistral-document-ai-2505",
        "document": {
            "type": document_type,
            document_type: data_url
        },
        "include_image_base64": True
    }

    # 发送请求
    response = requests.post(
        "https://chen9m1-deepseek-r1.services.ai.azure.com/providers/mistral/azure/ocr",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json=payload
    )

    return response.json()


# 使用示例
if __name__ == "__main__":
    # 处理 PDF 文件
    result = send_to_mistral_api("742-765.pdf", is_pdf=True)
    # write the result to a json file
    with open("mistral_api_response.json", "w", encoding="utf-8") as f:
        import json
        json.dump(result, f, ensure_ascii=False, indent=4)

    # 处理图像文件
    # result = send_to_mistral_api("your_image.jpg", is_pdf=False)
    # print(result)