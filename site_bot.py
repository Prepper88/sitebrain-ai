from typing import List
from pdf_parser import PDFParser, PDFParagraph
from vector_store import VectorStore
from cloud_llm import CloudLLM

class SiteBot:
    """
    SiteBot integrates PDF parsing, vector store, and LLM Q&A
    """
    def __init__(self):
        self.vector_store = VectorStore("all-MiniLM-L6-v2")

    def load_document(self, pdf_path: str):
        """
        Load a PDF document, parse it into paragraphs, and add to vector store
        """
        parser = PDFParser(pdf_path)
        parser.parse()
        # filter out type not text
        paragraphs = [p for p in parser.parse() if p.type == "text"]
        #paragraphs = parser.get_paragraphs()
        self.vector_store.add_paragraphs(paragraphs)
        print(f"Loaded {len(paragraphs)} paragraphs from {pdf_path}.")

    def ask_question(self, question: str, top_k: int = 10) -> str:
        """
        Ask a question:
        1. Search top-k relevant paragraphs
        2. Assemble prompt
        3. Call LLM
        """
        results: List[PDFParagraph] = self.vector_store.search(question, k=top_k)
        
        if not results:
            return "No relevant information found."

        # Assemble prompt
        context_texts = []
        for p in results:
            if p.type == "text":
                context_texts.append(p.content)
            elif p.type == "table":
                # Convert table DataFrame to CSV-style string
                context_texts.append(p.content.to_csv(index=False))
            else:
                context_texts.append(str(p.content))

        context = "\n\n".join(context_texts)
        prompt = f"Answer the following question based on the context:\n\nContext:\n{context}\n\nQuestion: {question}\nAnswer:"

        # Call CloudLLM
        # cloud_llm = CloudLLM(tokens=["hf_xxx"])  # Replace with actual tokens
        # answer = cloud_llm.generate(prompt)
        print(prompt)
        answer = "hahah"
        return answer

if __name__ == "__main__":
    bot = SiteBot()

    # Load a PDF document
    bot.load_document("docs/742-765.pdf")

    print("=== SiteBot Q&A (type 'exit' or 'quit' to stop) ===")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ["exit", "quit"]:
            print("Exiting SiteBot. Goodbye!")
            break

        answer = bot.ask_question(question)
        print("Answer:", answer)
        print("-" * 50)  
