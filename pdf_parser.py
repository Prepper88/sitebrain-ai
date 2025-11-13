from dataclasses import dataclass
from typing import List, Union
import pandas as pd
from unstructured.partition.pdf import partition_pdf


@dataclass
class PDFParagraph:
    """
    Data structure: Represents an intelligently recognized PDF paragraph element.
    
    This class encapsulates different types of content extracted from PDF documents,
    including titles, body text, tables, and other structural elements.
    """
    type: str                # Type of the paragraph: "title", "text", "table", etc.
    content: Union[str, pd.DataFrame]  # Content can be text string or DataFrame for tables

    def as_text(self) -> str:
        """
        Convert paragraph content to unified text format for embedding or processing.
        
        Returns:
            str: Text representation of the paragraph content
            - For text/title paragraphs: returns the original text content unchanged
            - For table paragraphs: converts DataFrame to CSV-style string
            - For other types: returns string representation
        
        Example:
            >>> text_para = PDFParagraph("text", "Hello world")
            >>> text_para.as_text()
            'Hello world'
            
            >>> table_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
            >>> table_para = PDFParagraph("table", table_df)
            >>> table_para.as_text()
            'A,B\\n1,3\\n2,4\\n'
        """
        if self.type == "text" or self.type == "title":
            return self.content
        elif self.type == "table" and isinstance(self.content, pd.DataFrame):
            # Convert DataFrame to CSV format without index for clean text representation
            return self.content.to_csv(index=False)
        else:
            # Fallback for any other content types
            return str(self.content)


class PDFParser:
    """
    PDF document parser using the Unstructured library for intelligent segmentation.
    
    This class automatically recognizes and extracts various structural elements
    from PDF documents such as titles, body text, tables, lists, and more.
    It converts the raw extraction results into structured PDFParagraph objects.
    
    Attributes:
        pdf_path (str): Path to the PDF file to be parsed
        paragraphs (List[PDFParagraph]): List of extracted paragraph objects
    """
    
    def __init__(self, pdf_path: str):
        """
        Initialize PDFParser with the target PDF file path.
        
        Args:
            pdf_path (str): Path to the PDF file to parse
        """
        self.pdf_path = pdf_path
        self.paragraphs: List[PDFParagraph] = []

    def parse(self) -> List[PDFParagraph]:
        """
        Parse the PDF document using Unstructured library and extract structured content.
        
        This method:
        1. Calls partition_pdf to intelligently parse the PDF document
        2. Categorizes elements into titles, text, tables, lists, etc.
        3. Converts tables from HTML to pandas DataFrames
        4. Stores all elements as PDFParagraph objects
        
        Returns:
            List[PDFParagraph]: List of parsed paragraph objects
            
        Example:
            >>> parser = PDFParser("document.pdf")
            >>> paragraphs = parser.parse()
            >>> print(f"Extracted {len(paragraphs)} elements")
            Extracted 45 elements
        """
        print(f"Parsing PDF file: {self.pdf_path}")
        
        # Use Unstructured library to extract elements from PDF
        # This returns a list of different element types (titles, tables, text, etc.)
        elements = partition_pdf(self.pdf_path)

        # Process each extracted element and convert to standardized format
        for element in elements:
            # Get element category or default to "Unknown" if not available
            category = element.category or "Unknown"
            # Extract and clean text content if available
            text = element.text.strip() if hasattr(element, "text") and element.text else ""

            # Handle table elements - convert HTML tables to DataFrames
            if category.lower() == "table" and hasattr(element, "metadata") and "text_as_html" in element.metadata:
                try:
                    # Unstructured represents tables as HTML, convert to pandas DataFrame
                    df = pd.read_html(element.metadata["text_as_html"])[0]
                    self.paragraphs.append(PDFParagraph(type="table", content=df))
                except Exception as table_error:
                    # Fallback: if table conversion fails, store as plain text
                    self.paragraphs.append(PDFParagraph(type="table", content=text))

            # Handle title elements
            elif category.lower() == "title":
                self.paragraphs.append(PDFParagraph(type="title", content=text))

            # Handle narrative text and list items
            elif category.lower() in ["narrativetext", "listitem"]:
                self.paragraphs.append(PDFParagraph(type="text", content=text))

            # Handle other element types (headers, footers, etc.) that have text content
            elif text:
                self.paragraphs.append(PDFParagraph(type=category.lower(), content=text))

        print(f"Parsing complete, extracted {len(self.paragraphs)} paragraphs/tables.")
        return self.paragraphs

    def get_tables_only(self) -> List[PDFParagraph]:
        """
        Extract and return only table elements from the parsed PDF.
        
        This function is currently not called but provides utility for table-specific processing.
        
        Returns:
            List[PDFParagraph]: List containing only table paragraphs
            
        Example:
            >>> tables = parser.get_tables_only()
            >>> print(f"Found {len(tables)} tables in the document")
        """
        return [para for para in self.paragraphs if para.type == "table"]

    def export_to_markdown(self, output_path: str) -> None:
        """
        Export parsed PDF content to Markdown format for easy reading and sharing.
        
        This function is currently not called but provides export functionality.
        
        Args:
            output_path (str): Path where the Markdown file will be saved
            
        Example:
            >>> parser.export_to_markdown("document.md")
            Exported PDF content to document.md
        """
        markdown_content = []
        
        for paragraph in self.paragraphs:
            if paragraph.type == "title":
                # Convert titles to Markdown headers
                markdown_content.append(f"# {paragraph.content}\n")
            elif paragraph.type == "table":
                # Convert tables to Markdown table format
                if isinstance(paragraph.content, pd.DataFrame):
                    markdown_content.append(paragraph.content.to_markdown(index=False))
                else:
                    markdown_content.append(f"```\n{paragraph.content}\n```")
                markdown_content.append("\n")
            elif paragraph.type == "text":
                # Regular text as paragraphs
                markdown_content.append(f"{paragraph.content}\n")
        
        # Write to Markdown file
        with open(output_path, 'w', encoding='utf-8') as md_file:
            md_file.write('\n'.join(markdown_content))
        
        print(f"Exported PDF content to {output_path}")


# Example usage (commented out to prevent execution)
if __name__ == "__main__":
    # Example of how to use the PDFParser class
    # parser = PDFParser("example.pdf")
    # paragraphs = parser.parse()
    
    # # Print summary of extracted content
    # for i, para in enumerate(paragraphs):
    #     print(f"{i+1}. [{para.type}] {para.content[:100]}...")
    
    # # tables = parser.get_tables_only()  # Extract only tables
    # # parser.export_to_markdown("output.md")  # Export to Markdown
    pass
