from dataclasses import dataclass
from typing import List, Union
import pandas as pd
from unstructured.partition.pdf import partition_pdf


@dataclass
class PDFParagraph:
    """数据结构：一个智能识别的 PDF 段落"""
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
    使用 Unstructured 库进行智能 PDF 分段解析。
    自动识别标题、正文、表格、列表等结构。
    """
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.paragraphs: List[PDFParagraph] = []

    def parse(self):
        """
        调用 unstructured.partition.pdf 智能解析 PDF 文档，
        并将结果转换为 PDFParagraph 对象列表。
        """
        print(f"🔍 正在解析 PDF 文件: {self.pdf_path}")
        elements = partition_pdf(self.pdf_path)

        for e in elements:
            category = e.category or "Unknown"
            text = e.text.strip() if hasattr(e, "text") and e.text else ""

            # 表格（Table）
            if category.lower() == "table" and hasattr(e, "metadata") and "text_as_html" in e.metadata:
                try:
                    # Unstructured的表格通常是HTML文本，可以转成DataFrame
                    df = pd.read_html(e.metadata["text_as_html"])[0]
                    self.paragraphs.append(PDFParagraph(type="table", content=df))
                except Exception:
                    self.paragraphs.append(PDFParagraph(type="table", content=text))

            # 标题
            elif category.lower() == "title":
                self.paragraphs.append(PDFParagraph(type="title", content=text))

            # 正文或列表
            elif category.lower() in ["narrativetext", "listitem"]:
                self.paragraphs.append(PDFParagraph(type="text", content=text))

            # 其他类型（页眉、页脚等）
            elif text:
                self.paragraphs.append(PDFParagraph(type=category.lower(), content=text))

        print(f"✅ 解析完成，共提取 {len(self.paragraphs)} 个段落/表格。")
        return self.paragraphs

