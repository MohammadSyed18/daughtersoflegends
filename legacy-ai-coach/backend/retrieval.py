"""Deterministic passage retrieval with corpus-aware scoring and page diversity."""

from collections import Counter
from hashlib import sha256
from math import log
import re, unicodedata


def tokens(text):
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return re.findall(r"\w+", normalized)


class PassageIndex:
    def __init__(self, chunks):
        self.passages = []
        self.frequency = Counter()
        seen = set()
        for chunk in chunks:
            body = chunk.get("text")
            page = chunk.get("page")
            if (
                not isinstance(body, str)
                or not body.strip()
                or type(page) is not int
                or page < 1
            ):
                raise ValueError("invalid passage")
            identity = (page, sha256(body.encode()).hexdigest())
            if identity in seen:
                continue
            seen.add(identity)
            terms = Counter(tokens(body))
            self.passages.append((dict(chunk), terms, sum(terms.values())))
            self.frequency.update(terms.keys())
        self.average_length = sum(length for _, _, length in self.passages) / max(
            1, len(self.passages)
        )

    def search(self, query, limit=5, max_per_page=2):
        if (
            not isinstance(query, str)
            or type(limit) is not int
            or not 1 <= limit <= 50
            or type(max_per_page) is not int
            or max_per_page < 1
        ):
            raise ValueError("invalid retrieval parameters")
        terms = set(tokens(query))
        ranked = []
        count = len(self.passages)
        for order, (passage, frequencies, length) in enumerate(self.passages):
            score = 0
            for term in terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                inverse = log(
                    1
                    + (count - self.frequency[term] + 0.5)
                    / (self.frequency[term] + 0.5)
                )
                score += (
                    inverse
                    * frequency
                    * 2.2
                    / (
                        frequency
                        + 1.2 * (0.25 + 0.75 * length / max(1, self.average_length))
                    )
                )
            if score > 0:
                ranked.append((score, order, passage))
        ranked.sort(key=lambda item: (-item[0], item[1]))
        pages = Counter()
        result = []
        for _, _, passage in ranked:
            if pages[passage["page"]] >= max_per_page:
                continue
            pages[passage["page"]] += 1
            result.append(dict(passage))
            if len(result) == limit:
                break
        return result
