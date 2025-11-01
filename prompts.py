def SEGMENT_PROMPT(context: str) -> str:
    return f"""
You are a document segmentation assistant designed to prepare Markdown documents
for use in a Retrieval-Augmented Generation (RAG) system.

Your goal is to segment the provided Markdown document into **semantically complete and independent paragraphs**.
Each paragraph should represent a coherent, self-contained unit of meaning that can be understood on its own.

### Guidelines:
1. **Semantic integrity first**:
   - Do not split logically related content.
   - For example, a subheading (e.g., "### PERMIT INFORMATION") and the table or text that follows it
     should be grouped together as a single paragraph.
   - Likewise, a section title with its explanation list or details should remain in the same paragraph.

2. **Output format**:
   Output the result as a **JSON array** of paragraph objects, where each object has:
   - `id`: a running number starting from 1 (e.g., 1, 2, 3, ...)
   - `type`: one of ["title", "section", "text", "table", "mixed"]
   - `content`: the Markdown text of that paragraph (preserve Markdown formatting)
   - `summary`: (optional, 1–2 sentences) a concise English summary of what the paragraph is about
   Additional requirements for JSON validity:
   - All backslashes (\) in the content must be properly escaped as \\.
   - Any double quotes (") inside string values must be escaped as \\".
   - No unescaped line breaks are allowed inside JSON strings; line breaks should be represented as \\n.
   - The JSON must remain fully parseable, with all objects and arrays properly closed.

The content may include complex text such as tables, formulas, or special symbols (e.g., LaTeX, Markdown), but it must not break JSON syntax.

3. **Formatting rules**:
   - Keep Markdown headings (`#`, `##`, `###`, etc.), lists, tables, and bold/italic styles intact.
   - Merge small fragments that belong together into one paragraph.
   - Each paragraph should be conceptually complete and not depend on another paragraph to make sense.
   - Prefer fewer but more meaningful chunks over too many fragmented ones.

Now, segment the following Markdown document into independent, semantically meaningful paragraphs:

{context}
"""

def RAG_QA_PROMPT(question: str, context: str) -> str:
    return f"""
            "Answer the following question based on the given context.\n\n"
            "The context below is in Markdown format, which may include numbered sections, headings, lists, tables, and formatted text.\n"
            "Each paragraph or section in the context may start with a number (e.g., '1.', '2.', '3.') indicating its order.\n\n"
            "When you answer, clearly indicate which numbered sections from the context your answer is based on.\n"
            "If multiple sections are relevant, list all their numbers.\n"
            "Format your final response as follows:\n"
            "Answer: <your answer>\n"
            "Based on sections: <numbers>\n\n"
            f"Context (Markdown):\n{context}\n\n"
            f"Question: {question}\n"
            "Answer:"
        """