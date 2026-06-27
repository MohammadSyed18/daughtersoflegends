import unittest
from context import build_context, query_coverage
from store_audit import audit_chunks, require_valid_store


class ContextTests(unittest.TestCase):
    def test_bounded_deduplicated_context_has_stable_sources(self):
        chunks = [
            {"page": 1, "text": "Vision and execution."},
            {"page": 1, "text": "Vision and execution."},
            {"page": 2, "text": "Discipline."},
        ]
        context = build_context(chunks, max_passages=2)
        self.assertEqual(len(context.passages), 2)
        self.assertLessEqual(len(context.rendered), 6000)
        self.assertEqual(
            context.passages[0].citation, build_context(chunks).passages[0].citation
        )
        self.assertEqual(
            query_coverage("What is execution?", context)["matched_terms"],
            ["execution"],
        )
        tiny = build_context(chunks, max_characters=5)
        self.assertEqual(tiny.passages, ())

    def test_metadata_and_embedding_corruption_are_reported(self):
        report = audit_chunks(
            [
                {"page": 1, "text": "One", "embedding": [1, 2]},
                {"page": 2, "text": "Two", "embedding": [3]},
            ]
        )
        self.assertFalse(report["valid"])
        with self.assertRaises(ValueError):
            require_valid_store([{"page": 0, "text": "Bad"}])
        with self.assertRaises(ValueError):
            require_valid_store(
                [{"page": 1, "text": "Bad", "embedding": [float("nan")]}]
            )
