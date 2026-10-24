import unittest

from src.memory.vector_store import tokenizar
from src.tools.database import KNOWLEDGE_BASE
from src.tools.search import retrieve


class SearchTests(unittest.TestCase):
    def test_tokenizar_removes_accents_and_short_tokens(self):
        self.assertEqual(tokenizar("Ação e vídeo!"), ["acao", "video"])

    def test_retrieve_returns_most_relevant_source_first(self):
        results = retrieve("método SIFT investigar a fonte")

        self.assertTrue(results)
        self.assertEqual(results[0]["fonte"], "Método SIFT")

    def test_retrieve_limits_number_of_results(self):
        self.assertLessEqual(len(retrieve("fake news informação", k=2)), 2)

    def test_retrieve_unknown_query_returns_no_sources(self):
        self.assertEqual(retrieve("zzqvxx"), [])

    def test_search_returns_original_knowledge_chunks(self):
        self.assertIs(
            retrieve("desordem informacional misinformation malinformation")[0],
            KNOWLEDGE_BASE[0],
        )


if __name__ == "__main__":
    unittest.main()
