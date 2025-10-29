from dataclasses import dataclass
from typing import List, Union
import pandas as pd
from unstructured.partition.pdf import partition_pdf


@dataclass
class PDFParagraph:
    """Data structure: A smartly recognized PDF paragraph"""
    type: str                # e.g., "title", "text", "table"
    content: Union[str, pd.DataFrame]

    def as_text(self) -> str:
        """
        Convert paragraph content to text for embedding.
        Text paragraph → unchanged
        Table paragraph → convert DataFrame to CSV-style string
        """
        if self.type == "text" or self.type == "title":
            return self.content
        elif self.type == "table" and isinstance(self.content, pd.DataFrame):
            return self.content.to_csv(index=False)
        else:
            return str(self.content)


class PDFParser:
    """
    Use the Unstructured library for intelligent PDF segmentation.
    Automatically recognizes structures such as titles, body text, tables, and lists.
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.paragraphs: List[PDFParagraph] = []

    def parse(self):
        """
        Call unstructured.partition.pdf to intelligently parse the PDF document,
        and convert the results into a list of PDFParagraph objects.
        """
        print(f"🔍 Parsing PDF file: {self.pdf_path}")
        elements = partition_pdf(self.pdf_path)

        for e in elements:
            category = e.category or "Unknown"
            text = e.text.strip() if hasattr(e, "text") and e.text else ""

            # Table
            if category.lower() == "table" and hasattr(e, "metadata") and "text_as_html" in e.metadata:
                try:
                    # Unstructured tables are usually HTML text and can be converted to DataFrame
                    df = pd.read_html(e.metadata["text_as_html"])[0]
                    self.paragraphs.append(PDFParagraph(type="table", content=df))
                except Exception:
                    self.paragraphs.append(PDFParagraph(type="table", content=text))

            # Title
            elif category.lower() == "title":
                self.paragraphs.append(PDFParagraph(type="title", content=text))

            # Body text or list
            elif category.lower() in ["narrativetext", "listitem"]:
                self.paragraphs.append(PDFParagraph(type="text", content=text))

            # Other types (headers, footers, etc.)
            elif text:
                self.paragraphs.append(PDFParagraph(type=category.lower(), content=text))

        print(f"✅ Parsing complete, extracted {len(self.paragraphs)} paragraphs/tables.")
        return self.paragraphs

