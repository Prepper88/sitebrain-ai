from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from typing import List, Union
import pandas as pd
from pdf_parser import PDFParagraph

class VectorStore:
    """
    Vector store using MiniLM + FAISS, supporting PDFParagraphs
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.dim)  # inner product for cosine similarity
        self.paragraphs: List[PDFParagraph] = []  # store PDFParagraph objects
        print(f"✅ Loaded model: {model_name} (dimension={self.dim})")

    def add_paragraphs(self, paragraphs: List[PDFParagraph]):
        """
        Add a list of PDFParagraph objects to the vector store
        """
        if not paragraphs:
            return

        # Convert all paragraphs to text for embedding
        texts = [p.as_text() for p in paragraphs]

        # Encode embeddings
        embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

        # Add to FAISS index
        self.index.add(embeddings)

        # Store original PDFParagraph objects
        self.paragraphs.extend(paragraphs)

    def search(self, query: str, k: int = 3) -> List[PDFParagraph]:
        """
        Search top-k similar paragraphs for a query string
        Returns list of PDFParagraph objects
        """
        if self.index.ntotal == 0:
            return []

        # Encode query
        query_vec = self.model.encode([query], convert_to_numpy=True, normalize_embeddings=True)

        # Search index
        D, I = self.index.search(query_vec, k)
        results = []
        for idx in I[0]:
            if idx < len(self.paragraphs):
                results.append(self.paragraphs[idx])
        

        for i, p in enumerate(results, 1):
            print("================================")
            print(f"Rank {i}: score={D[0][i-1]}, content preview={str(p.content)[:1000]}")
        return results

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    # Example PDFParagraphs
    import pandas as pd
    paras = [
        PDFParagraph("text", "This is the first paragraph about AI."),
        PDFParagraph("text", "Another paragraph discussing RAG techniques."),
        PDFParagraph("table", pd.DataFrame({"Col1": [1,2], "Col2": ["A","B"]}))
    ]

    store = VectorStore()
    store.add_paragraphs(paras)

    # Query
    query = "what's the first paragraph about?"
    results = store.search(query, k=2)

    for i, p in enumerate(results, 1):
        print(f"Rank {i}: type={p.type}, content preview={str(p.content)[:100]}")
