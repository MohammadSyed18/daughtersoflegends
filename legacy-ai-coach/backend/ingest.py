"""
Builds a local knowledge base from data/book.pdf.

For production-quality semantic search, run this after setting OPENAI_API_KEY.
If no key is provided, the app can still run in DEMO_MODE using keyword retrieval.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from pypdf import PdfReader
from openai import OpenAI

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
BOOK_PATH = DATA_DIR / "book.pdf"
STORE_PATH = Path(__file__).resolve().parent / "vector_store.json"
EMBED_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_pdf_pages(pdf_path: Path) -> List[Dict[str, Any]]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing PDF at {pdf_path}")
    reader = PdfReader(str(pdf_path))
    pages = []
    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        text = clean_text(text)
        if text:
            pages.append({"page": i, "text": text})
    return pages


def chunk_pages(pages: List[Dict[str, Any]], max_words: int = 220, overlap: int = 45) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    for page in pages:
        words = page["text"].split()
        start = 0
        while start < len(words):
            end = min(start + max_words, len(words))
            chunk_text = " ".join(words[start:end]).strip()
            if len(chunk_text) > 80:
                chunks.append({"id": f"p{page['page']}_c{len(chunks)+1}", "page": page["page"], "text": chunk_text})
            if end == len(words):
                break
            start = max(0, end - overlap)
    return chunks


def embed_texts(texts: List[str]) -> List[List[float]]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "replace_with_your_openai_api_key":
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to backend/.env or hosting environment.")
    client = OpenAI(api_key=api_key)
    embeddings: List[List[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        response = client.embeddings.create(model=EMBED_MODEL, input=batch)
        embeddings.extend([item.embedding for item in response.data])
    return embeddings


def main() -> None:
    pages = extract_pdf_pages(BOOK_PATH)
    chunks = chunk_pages(pages)
    print(f"Extracted {len(pages)} pages and created {len(chunks)} chunks.")
    embeddings = embed_texts([c["text"] for c in chunks])
    for chunk, embedding in zip(chunks, embeddings):
        chunk["embedding"] = embedding
    STORE_PATH.write_text(json.dumps({"chunks": chunks}, ensure_ascii=False), encoding="utf-8")
    print(f"Saved knowledge base to {STORE_PATH}")


if __name__ == "__main__":
    main()
