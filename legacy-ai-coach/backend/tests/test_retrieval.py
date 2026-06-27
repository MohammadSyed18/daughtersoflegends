import unittest
from retrieval import PassageIndex


class Retrieval(unittest.TestCase):
    def test_unrelated_questions_return_no_false_source(self):
        index = PassageIndex(
            [{"page": 1, "text": "Vision and execution build a legacy."}]
        )
        self.assertEqual(index.search("unrelated astronomy"), [])

    def test_duplicate_chunks_are_not_double_counted(self):
        chunk = {"page": 1, "text": "Vision and execution."}
        index = PassageIndex([chunk, chunk])
        self.assertEqual(len(index.search("vision")), 1)

    def test_page_diversity_and_immutable_results(self):
        index = PassageIndex(
            [{"page": 1, "text": f"Execution strategy item {i}"} for i in range(4)]
            + [{"page": 2, "text": "Execution strategy next action"}]
        )
        results = index.search("execution strategy", max_per_page=1)
        self.assertEqual({x["page"] for x in results}, {1, 2})
        results[0]["text"] = "changed"
        self.assertNotEqual(index.search("execution strategy")[0]["text"], "changed")
