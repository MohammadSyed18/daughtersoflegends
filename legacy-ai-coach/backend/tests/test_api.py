import os, unittest
from types import SimpleNamespace
from unittest.mock import patch

with patch.dict(os.environ, {"DEMO_MODE": "true", "OPENAI_API_KEY": ""}):
    import app
    import ingest
from fastapi.testclient import TestClient


class API(unittest.TestCase):
    def test_question_limits_and_no_match_response(self):
        with TestClient(app.app) as client:
            self.assertEqual(
                client.post("/chat", json={"message": "x" * 4001}).status_code, 422
            )
            self.assertEqual(
                client.post("/chat", json={"message": "   "}).status_code, 400
            )
            response = client.post("/chat", json={"message": "quasarquuxxyz"})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["sources"], [])

    def test_chunk_overlap_must_make_progress(self):
        with self.assertRaises(ValueError):
            ingest.chunk_pages([{"page": 1, "text": "words"}], 10, 10)

    def test_embedding_batch_is_reordered_by_input_index(self):
        response = SimpleNamespace(
            data=[
                SimpleNamespace(index=1, embedding=[2.0]),
                SimpleNamespace(index=0, embedding=[1.0]),
            ]
        )
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test"}), patch.object(
            ingest, "OpenAI"
        ) as constructor:
            constructor.return_value.embeddings.create.return_value = response
            self.assertEqual(ingest.embed_texts(["one", "two"]), [[1.0], [2.0]])
