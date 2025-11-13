import base64
import requests
import os


def document_to_base64(file_path):
    """
    Convert any file to base64 encoded string for transmission over HTTP
    
    Args:
        file_path (str): Path to the file to be converted
        
    Returns:
        str: Base64 encoded string representation of the file
    """
    # Open file in binary read mode to handle all file types
    with open(file_path, "rb") as file:
        # Read the entire file content as bytes
        file_data = file.read()
        # Encode the binary data to base64, then decode to UTF-8 string for JSON compatibility
        base64_encoded = base64.b64encode(file_data).decode('utf-8')
    return base64_encoded


def send_to_mistral_api(file_path, is_pdf=True):
    """
    Send document to Mistral Document AI API for OCR and document processing
    
    Args:
        file_path (str): Path to the document file (PDF or image)
        is_pdf (bool): True if file is PDF, False if image (default: True)
        
    Returns:
        dict: API response containing extracted text and document analysis results
    """

    # API key for authentication with Mistral services
    # Note: In production, consider using environment variables for security
    api_key = "8Z7g2A07b2ItypQ2JOhMTwzQiKCcC4t657j3mWeqhMUtL4ZLYgcWJQQJ99BIACHYHv6XJ3w3AAAAACOGtDyz"

    # Convert the document file to base64 format for API transmission
    base64_content = document_to_base64(file_path)

    # Determine the document type and format the data URL accordingly
    # Mistral API expects different parameters for PDF vs image files
    if is_pdf:
        document_type = "document_url"  # Parameter name for PDF documents
        # Create data URL with PDF MIME type and base64 content
        data_url = f"data:application/pdf;base64,{base64_content}"
    else:
        document_type = "image_url"     # Parameter name for image documents
        # Create data URL with JPEG MIME type and base64 content
        # Note: For other image formats, you may need to adjust the MIME type
        data_url = f"data:image/jpeg;base64,{base64_content}"

    # Construct the request payload according to Mistral API specifications
    payload = {
        "model": "mistral-document-ai-2505",  # Specific document AI model version
        "document": {
            "type": document_type,  # Document type identifier
            document_type: data_url  # Dynamic key based on document type containing the data URL
        },
        "include_image_base64": True  # Request that base64 images be included in response
    }

    # Make POST request to Mistral Document AI API endpoint
    response = requests.post(
        # Azure-hosted Mistral OCR service endpoint
        "https://chen9m1-deepseek-r1.services.ai.azure.com/providers/mistral/azure/ocr",
        headers={
            "Content-Type": "application/json",  # Specify JSON content type
            "Authorization": f"Bearer {api_key}"  # Bearer token authentication
        },
        json=payload  # Automatically serialize payload to JSON
    )

    # Return parsed JSON response from the API
    return response.json()


# Main execution block - runs when script is executed directly
if __name__ == "__main__":
    # Example 1: Process a PDF document
    # Send PDF file to Mistral API for text extraction and analysis
    result = send_to_mistral_api("742-765.pdf", is_pdf=True)
    
    # Save the API response to a JSON file for later analysis
    with open("mistral_api_response.json", "w", encoding="utf-8") as f:
        import json
        # Write JSON response with proper formatting:
        # - ensure_ascii=False: Preserve non-ASCII characters (Chinese, etc.)
        # - indent=4: Pretty-print with 4-space indentation for readability
        json.dump(result, f, ensure_ascii=False, indent=4)
    
    print("PDF processing completed. Results saved to mistral_api_response.json")

    # Example 2: Process an image file (commented out - remove # to use)
    # Uncomment the following lines to process an image file instead:
    # result = send_to_mistral_api("your_image.jpg", is_pdf=False)
    # print("Image processing result:", result)
    
    # The response typically contains:
    # - Extracted text content
    # - Document structure information  
    # - Confidence scores for OCR accuracy
    # - Page-level metadata and layout analysis
