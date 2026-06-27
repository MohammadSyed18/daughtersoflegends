"""Bounded reference context and inspectable retrieval coverage."""

from dataclasses import dataclass
from hashlib import sha256
import json
import re


@dataclass(frozen=True)
class ContextPassage:
    citation: str
    page: int
    text: str


@dataclass(frozen=True)
class EvidenceContext:
    passages: tuple[ContextPassage, ...]
    rendered: str
    omitted: int


def build_context(chunks, *, max_characters=6000, max_passages=3, per_passage=1800):
    if any(
        type(value) is not int or value < 1
        for value in (max_characters, max_passages, per_passage)
    ):
        raise ValueError("positive context limits required")
    passages, rendered, seen = [], [], set()
    used = 0
    for chunk in chunks:
        page, text = chunk.get("page"), chunk.get("text")
        if (
            type(page) is not int
            or page < 1
            or not isinstance(text, str)
            or not text.strip()
        ):
            raise ValueError("invalid context passage")
        identity = (page, sha256(text.encode()).hexdigest())
        if identity in seen:
            continue
        seen.add(identity)
        if len(passages) >= max_passages:
            continue
        citation = f"p{page}-{identity[1][:8]}"
        excerpt = text.strip()[:per_passage]
        # JSON serialization bounds metadata and prevents delimiter-shaped text
        # from creating a new structural record in the context representation.
        record = json.dumps(
            {"citation": citation, "page": page, "excerpt": excerpt}, ensure_ascii=False
        )
        if used + len(record) > max_characters:
            continue
        passages.append(ContextPassage(citation, page, excerpt))
        rendered.append(record)
        used += len(record) + 1
    return EvidenceContext(
        tuple(passages), "\n".join(rendered), len(chunks) - len(passages)
    )


def query_coverage(query, context):
    terms = set(re.findall(r"\w+", query.casefold()))
    stop = {"the", "a", "and", "is", "of", "to", "in", "how", "what", "i", "my"}
    terms -= stop
    found = set(
        re.findall(r"\w+", " ".join(item.text for item in context.passages).casefold())
    )
    matched = sorted(terms & found)
    return {
        "query_terms": len(terms),
        "matched_terms": matched,
        "lexical_coverage": len(matched) / len(terms) if terms else 0,
        "source_pages": sorted({item.page for item in context.passages}),
        "note": "Lexical overlap describes retrieval coverage; it is not an answer-correctness probability.",
    }
