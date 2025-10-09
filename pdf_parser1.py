import pdfplumber
import pandas as pd
from typing import List, Dict, Union

class PDFParagraph:
    """
    PDF Paragraph object
    type: 'text', 'table', or other types for future extension
    content: text content or table content
    """
    def __init__(self, type_: str, content: Union[str, pd.DataFrame]):
        self.type = type_
        self.content = content

    def to_dict(self):
        if self.type == "table" and isinstance(self.content, pd.DataFrame):
            # Convert table to list of lists for JSON serialization
            content = self.content.values.tolist()
        else:
            content = self.content
        return {"type": self.type, "content": content}
    
    def as_text(self) -> str:
        """
        Convert paragraph content to text for embedding.
        Text paragraph → unchanged
        Table paragraph → convert DataFrame to CSV-style string
        """
        if self.type == "text":
            return self.content
        elif self.type == "table" and isinstance(self.content, pd.DataFrame):
            return self.content.to_csv(index=False)
        else:
            return str(self.content)


class PDFParser:
    """
    PDF Parser class
    Extracts paragraphs from PDF including text and tables
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.paragraphs: List[PDFParagraph] = []

    def parse(self):
        """
        Parse the PDF file
        Extracts text paragraphs by double newline
        Extracts tables as table paragraphs
        """
        all_text = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                # 1️⃣ Parse text paragraphs
                text = page.extract_text()
                if text:
                    all_text.append(text)

                # 2️⃣ Parse table paragraphs
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    self.paragraphs.append(PDFParagraph(type_="table", content=df))
        
        full_text = "\n".join(all_text)
        # write full_text to a txt file for debugging
        with open("debug_full_text.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
            
        text_paras = [p.strip() for p in full_text.split("\n\n") if p.strip()]
        for para in text_paras:
            self.paragraphs.append(PDFParagraph(type_="text", content=para))

    def get_paragraphs(self) -> List[PDFParagraph]:
        """Return the list of PDFParagraph objects"""
        return self.paragraphs

    def to_json(self) -> List[Dict]:
        """Return JSON-serializable list of paragraphs"""
        return [p.to_dict() for p in self.paragraphs]


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    parser = PDFParser("docs/742-765.pdf")
    parser.parse()
    paragraphs = parser.get_paragraphs()

    # Print paragraph type and first 100 characters
    for i, p in enumerate(paragraphs, 1):
        if p.type == "text":
            print(f"{i}. [TEXT] {p.content[:100]}...")
        elif p.type == "table":
            print(f"{i}. [TABLE] {p.content.shape} table rows/columns...")

    # Save paragraphs to JSON file
    import json
    with open("pdf_paragraphs.json", "w", encoding="utf-8") as f:
        json.dump(parser.to_json(), f, ensure_ascii=False, indent=2)
