"""Knowledge-store integrity checks without exposing book passage text."""

from collections import Counter
from hashlib import sha256
import math


def audit_chunks(chunks):
    if not isinstance(chunks, list):
        raise ValueError("chunks must be an array")
    errors, warnings, pages, seen, dimensions = [], [], Counter(), set(), set()
    embedded = 0
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, dict):
            errors.append(f"chunk {index}: expected object")
            continue
        page, body = chunk.get("page"), chunk.get("text")
        if (
            type(page) is not int
            or page < 1
            or not isinstance(body, str)
            or not body.strip()
        ):
            errors.append(f"chunk {index}: invalid page or text")
            continue
        pages[page] += 1
        identity = (page, sha256(body.encode()).hexdigest())
        if identity in seen:
            warnings.append(f"chunk {index}: duplicate page/text")
        seen.add(identity)
        vector = chunk.get("embedding")
        if vector is not None:
            if (
                not isinstance(vector, list)
                or not vector
                or any(
                    type(value) not in (int, float) or not math.isfinite(value)
                    for value in vector
                )
            ):
                errors.append(f"chunk {index}: invalid embedding")
            else:
                embedded += 1
                dimensions.add(len(vector))
                if not any(vector):
                    warnings.append(f"chunk {index}: zero embedding")
    if len(dimensions) > 1:
        errors.append("embedding dimensions differ")
    if embedded and embedded != len(chunks):
        warnings.append("store mixes embedded and keyword-only passages")
    return {
        "valid": not errors,
        "chunks": len(chunks),
        "pages": len(pages),
        "embedded_chunks": embedded,
        "embedding_dimensions": sorted(dimensions),
        "chunks_per_page": dict(sorted(pages.items())),
        "errors": errors,
        "warnings": warnings,
    }


def require_valid_store(chunks):
    report = audit_chunks(chunks)
    if not report["valid"]:
        raise ValueError("; ".join(report["errors"]))
    return report
