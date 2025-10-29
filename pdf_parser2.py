# pip install pymupdf spacy sentence-transformers chromadb
import fitz  # PyMuPDF
import re
import spacy
from typing import List, Dict

nlp = spacy.load("en_core_web_sm")  # 用于分句

def extract_blocks(pdf_path: str):
    doc = fitz.open(pdf_path)
    results = []
    for page_no in range(len(doc)):
        page = doc[page_no]
        blocks = page.get_text("dict")["blocks"]  # blocks include bbox and lines
        for b in blocks:
            text = ""
            for line in b.get("lines", []):
                for span in line.get("spans", []):
                    text += span.get("text", "")
            # keep bbox and maybe max font size in block
            max_fontsize = max((span.get("size",0) for line in b.get("lines",[]) for span in line.get("spans",[])), default=0)
            bbox = b.get("bbox", None)
            results.append({"page": page_no+1, "text": text.strip(), "bbox": bbox, "font_size": max_fontsize})
    return results

def detect_headings(blocks):
    # heuristic: large font size or all caps short text => heading
    font_sizes = [b['font_size'] for b in blocks if b['font_size']>0]
    avg_fs = sum(font_sizes)/len(font_sizes) if font_sizes else 0
    for b in blocks:
        text = b['text']
        is_heading = b['font_size'] >= avg_fs*1.1 or (len(text.split())<=6 and text.isupper())
        b['is_heading'] = is_heading
    return blocks

def extract_kv_from_blocks(blocks):
    # basic regex-based key extraction
    text_all = "\n".join([f"PAGE{b['page']}: {b['text']}" for b in blocks])
    kv = {}
    m = re.search(r"Permit number\s*[:\n]*\s*([0-9]{4}\s*[0-9]{6}\s*\w+)", text_all, re.I)
    if m: kv['permit_number'] = m.group(1).strip()
    m = re.search(r"Address\s*[:\n]*\s*([A-Z0-9\-\s\.]+(?:AVE|RD|ST|BLVD|DR|COURT)?)", text_all, re.I)
    if m: kv['address'] = m.group(1).strip()
    # more rules...
    return kv

def split_to_chunks(blocks, max_tokens=400, overlap_tokens=50):
    chunks = []
    for b in blocks:
        # skip tiny or headings-only blocks if needed
        doc = nlp(b['text'])
        sents = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        # sliding window join sentences into token-ish chunks
        cur = []
        cur_len = 0
        for s in sents:
            tlen = len(s.split())
            if cur_len + tlen > max_tokens and cur:
                chunks.append({"text":" ".join(cur), "page": b['page'], "bbox": b['bbox']})
                # overlap: keep last few sentences
                if overlap_tokens>0:
                    # keep last sentences until overlap size reached
                    overlap = []
                    ol = 0
                    while cur and ol < overlap_tokens:
                        last = cur.pop()
                        overlap.insert(0, last)
                        ol += len(last.split())
                    cur = overlap
                    cur_len = sum(len(x.split()) for x in cur)
                else:
                    cur = []
                    cur_len = 0
            cur.append(s)
            cur_len += tlen
        if cur:
            chunks.append({"text":" ".join(cur), "page": b['page'], "bbox": b['bbox']})
    return chunks

# usage
blocks = extract_blocks("742-765.pdf")
print(f"Extracted {len(blocks)} text blocks from PDF.")

blocks = detect_headings(blocks)
kv = extract_kv_from_blocks(blocks)  # includes permit_number, address ...
chunks = split_to_chunks(blocks, max_tokens=350, overlap_tokens=60)
# attach metadata
for c in chunks:
    c['metadata'] = {"permit_number": kv.get('permit_number'), "page": c['page']}
# 然后对 chunks 生成 embeddings 并入库（FAISS/Chroma）...

