import json
from typing import List
from pdf_parser_mistral import PDFParser, PDFParagraph
from vector_store import VectorStore
from cloud_llm import CloudLLM
from prompts import RAG_QA_PROMPT
import pandas as pd

class SiteBot:
    """
    SiteBot integrates PDF parsing, vector store, and LLM Q&A
    """
    def __init__(self):
        self.vector_store = VectorStore("all-MiniLM-L6-v2")
        self.pdf_parser = PDFParser()
        self.cloud_llm = CloudLLM()

    def load_document(self, pdf_path: str):
        """
        Load a PDF document, parse it into paragraphs, and add to vector store
        """
        paragraphs = self.pdf_parser.parse(pdf_path=pdf_path)
        # filter out type not text
        paragraphs = [p for p in paragraphs if p.type != "table"]
        #paragraphs = parser.get_paragraphs()
        self.vector_store.add_paragraphs(paragraphs)
        print(f"Loaded {len(paragraphs)} paragraphs from {pdf_path}.")

    def load_documents(self, pdf_path: str):
        """
        Load multiple PDF documents from a directory
        """
        import os
        for filename in os.listdir(pdf_path):
            if filename.lower().endswith(".pdf"):
                full_path = os.path.join(pdf_path, filename)
                self.load_document(full_path)

    def ask_question(self, question: str, top_k: int = 5) -> str:
        """
        Ask a question:
        1. Search top-k relevant paragraphs
        2. Assemble prompt
        3. Call LLM
        """
        related_chunks: List[PDFParagraph] = self.vector_store.search(question, k=top_k)
        
        if not related_chunks:
            return "No relevant information found."

        # Assemble prompt
        context_texts = []
        # append index before content
        for p in related_chunks:
            chunk  = p["chunk"]
            if chunk.type == "text":
                context_texts.append(f"{len(context_texts) + 1}. {chunk.content}")
            elif chunk.type == "table":
                # Convert table DataFrame to CSV-style string
                context_texts.append(f"{len(context_texts) + 1}. {chunk.content.to_csv(index=False)}")
            else:
                context_texts.append(f"{len(context_texts) + 1}. {str(chunk.content)}")

        context = "\n\n".join(context_texts)
        prompt = RAG_QA_PROMPT(question, context)
        # Call CloudLLM
        answer = self.cloud_llm.generate(prompt)
        #print(prompt)
        response = {
            "question": question,
            "answer": answer,
            "related_chunks": related_chunks
        }
        return response 

def default_serializer(obj):
    if isinstance(obj, PDFParagraph):
        return obj.to_dict()
    if isinstance(obj, pd.DataFrame):
        return obj.values.tolist()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


if __name__ == "__main__":
    bot = SiteBot()

    # Load a PDF document
    bot.load_documents("docs/")
    #bot.load_document("docs/742-765.pdf")

    print("=== SiteBot Q&A (type 'exit' or 'quit' to stop) ===")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("Exiting SiteBot. Goodbye!")
            break

        response = bot.ask_question(question)
        print("response:\n", json.dumps(response, default=default_serializer, indent=2))
        print("-" * 50)  
