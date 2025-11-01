import json
import os
import base64
import requests
from dataclasses import dataclass
from typing import List, Union
import pandas as pd
from unstructured.partition.pdf import partition_pdf
from cloud_llm import CloudLLM
from prompts import SEGMENT_PROMPT
import re
import config


@dataclass
class PDFParagraph:
    """Data structure: A smartly recognized PDF paragraph"""
    type: str                # e.g., "title", "text", "table"
    content: Union[str, pd.DataFrame]
    doc: str = ""        # Document source (optional)
    page_number: int = -1  # Page number (optional)

    def as_text(self) -> str:
        """
        Convert paragraph content to text for embedding.
        Text paragraph → unchanged
        Table paragraph → convert DataFrame to CSV-style string
        """
        if self.type == "table" and isinstance(self.content, pd.DataFrame):
            return self.content.to_csv(index=False)
        else:
            return str(self.content)

    def to_dict(self):
        if self.type == "table" and isinstance(self.content, pd.DataFrame):
            # Convert table to list of lists for JSON serialization
            content = self.content.values.tolist()
        else:
            content = self.content
        return {"type": self.type, "content": content, "doc": self.doc, "page_number": self.page_number}

class PDFParser:
    def __init__(self, api_key=config.AZURE_API_KEY):
        """
        Initialize PDFParser
        :param api_key: Mistral API key
        """
        self.api_key = api_key
        self.api_url = config.AZURE_DOC_LLM_ENDPOINT
        self.cloud_llm = CloudLLM(True)
        self.chunks_dir = "chunks"

    @staticmethod
    def document_to_base64(file_path):
        """Convert document to base64 string"""
        with open(file_path, "rb") as file:
            return base64.b64encode(file.read()).decode("utf-8")

    def send_to_mistral_api(self, file_path, is_pdf=True):
        """Send file to Mistral OCR API and return parsing results"""
        base64_content = self.document_to_base64(file_path)

        if is_pdf:
            document_type = "document_url"
            data_url = f"data:application/pdf;base64,{base64_content}"
        else:
            document_type = "image_url"
            data_url = f"data:image/jpeg;base64,{base64_content}"

        payload = {
            "model": "mistral-document-ai-2505",
            "document": {
                "type": document_type,
                document_type: data_url
            },
            "include_image_base64": True
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.post(self.api_url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

    def parse(self, pdf_path):
        """
        Parse PDF file and return a list of paragraphs.
        Each page's markdown content is treated as a single paragraph.
        """
        print(f"Parsing file: {pdf_path}")

        paragraphs = []

        # check if file exists under chunks/, if exists, load from there
        chunk_file_path = get_chunk_file_path(pdf_path)
        chunk_recovery_file_path = get_recovery_file_path(pdf_path)

        start_page_number = 1
        if os.path.exists(chunk_file_path):
            with open(chunk_file_path, "r", encoding="utf-8") as f:
                cached_paragraphs = json.load(f)
            print(f"Loaded {len(cached_paragraphs)} paragraphs from cached chunk file.")
            return [PDFParagraph(**p) for p in cached_paragraphs]
        elif os.path.exists(chunk_recovery_file_path):
            print(f"Found recovery file {chunk_recovery_file_path}, resuming parsing.")
            with open(chunk_recovery_file_path, "r", encoding="utf-8") as f:
                cached_paragraphs = json.load(f)
            paragraphs = [PDFParagraph(**p) for p in cached_paragraphs]

            # find max page number
            max_page_number = 0
            for p in paragraphs:
                if p.page_number > max_page_number:
                    max_page_number = p.page_number
            start_page_number = max_page_number + 1
            print(f"Resuming {max_page_number} pages from recovery file {chunk_recovery_file_path} with {len(paragraphs)} paragraphs.")
            
        # parse all pages from Mistral API
        result = self.send_to_mistral_api(pdf_path, is_pdf=True)

        pages = result.get("pages", [])
        try:
            for page in pages[start_page_number - 1:]:
                markdown = page.get("markdown", "").strip()
                if (markdown == ""):
                    print(f"Skipping empty markdown on page {page_number}")
                    continue
                page_number = page.get("index", -1) + 1
                prompt = SEGMENT_PROMPT(markdown)
                response = self.cloud_llm.generate(prompt)

                if config.DEBUG:
                    # Save raw response for debugging
                    debug_dir = "debug_mistral"
                    os.makedirs(debug_dir, exist_ok=True)
                    document_name = os.path.basename(pdf_path).replace(".pdf", "")
                    os.makedirs(os.path.join(debug_dir, document_name), exist_ok=True)
                    with open(os.path.join(debug_dir, document_name, f"page_{page_number}_prompt.md"), "w", encoding="utf-8") as f:
                        f.write(prompt)
                    with open(os.path.join(debug_dir, document_name, f"page_{page_number}_response.txt"), "w", encoding="utf-8") as f:
                        f.write(response)

                try:
                    json_response = extract_json(response)

                    if json_response is None:
                        print(f"Skipping page {page_number} due to no JSON response")
                        continue

                    segmented = json_response
                    for item in segmented:
                        p_type = item.get("type", "text")
                        content = item.get("content", "")
                        paragraphs.append(PDFParagraph(type=p_type, content=content, doc=pdf_path, page_number=page_number))
                except json.JSONDecodeError:
                    print(f"JSON parsing error, skipping content on page {page_number}")
        except Exception as e:
            print(f"Error during parsing: {e}")
            # Save recovery file
            save_recovery_file(pdf_path, paragraphs)
            return paragraphs

        # Save paragraphs to chunk/<document_name>.json
        save_chunk_file(pdf_path, paragraphs)
        # Delete recovery file if exists
        delete_recovery_file(pdf_path)
        
        print(f"Total {len(paragraphs)} paragraphs parsed from {pdf_path}.")
        return paragraphs

def get_chunk_file_path(pdf_path):
    """Get chunk file path for a given PDF"""
    document_name = os.path.basename(pdf_path).replace(".pdf", ".json")
    chunk_file_path = os.path.join("chunks", document_name)
    return chunk_file_path

def get_recovery_file_path(pdf_path):
    """Get recovery file path for a given PDF"""
    document_recovery_name = os.path.basename(pdf_path).replace(".pdf", "-recovery.json")
    chunk_recovery_file_path = os.path.join("chunks", document_recovery_name)
    return chunk_recovery_file_path

def save_recovery_file(pdf_path, paragraphs):
    """Save recovery file during parsing"""
    os.makedirs("chunks", exist_ok=True)
    chunk_recovery_file_path = get_recovery_file_path(pdf_path)
    with open(chunk_recovery_file_path, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in paragraphs], f, ensure_ascii=False, indent=4)

def save_chunk_file(pdf_path, paragraphs):
    """Save chunk file after successful parsing"""
    os.makedirs("chunks", exist_ok=True)
    chunk_file_path = get_chunk_file_path(pdf_path)
    with open(chunk_file_path, "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in paragraphs], f, ensure_ascii=False, indent=4)

def delete_recovery_file(pdf_path):
    """Delete recovery file if exists after successful parsing"""
    chunk_recovery_file_path = get_recovery_file_path(pdf_path)
    if os.path.exists(chunk_recovery_file_path):
        os.remove(chunk_recovery_file_path)
        print(f"Deleted recovery file {chunk_recovery_file_path}.")

def extract_json(text: str):
    """
    Extract and parse JSON content from a string.
    Automatically removes Markdown code fences like ```json ... ``` if present.

    :param text: Raw string containing JSON (possibly wrapped in ```json)
    :return: Parsed Python object (list or dict)
    """
    # 1. Try to find JSON inside ```json ... ```
    match = re.search(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        # If no code fence, try to capture top-level JSON brackets {} or []
        match = re.search(r"(\{.*\}|\[.*\])", text, flags=re.DOTALL)
        if not match:
            # print warning and return empty
            print("⚠️ No JSON content found in the text.")
            return None
        json_str = match.group(1)

    # 2. Attempt to parse the JSON string
    try:
        data = json.loads(json_str)
        return data
    except json.JSONDecodeError as e:
        print("⚠️ JSON parsing failed:", e)
        print("Snippet of extracted text:\n", json_str[:500])
        raise

# Sample usage
if __name__ == "__main__":
    parser = PDFParser()

    pdf_file = "742-765.pdf"
    paragraphs = parser.parse(pdf_file)

    # Output results to JSON file
    with open("parsed_paragraphs.json", "w", encoding="utf-8") as f:
        json.dump([p.to_dict() for p in paragraphs], f, ensure_ascii=False, indent=4)


    print("Parsing complete, results saved to parsed_paragraphs.json")
