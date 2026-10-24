import json
import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

import api
from src.agent.core import AnthropicAPIError, MissingAPIKeyError, ask
from src.tools.database import KNOWLEDGE_BASE


class AgentTests(unittest.TestCase):
    def test_ask_requires_api_key(self):
        with patch("src.agent.core.API_KEY", None):
            with self.assertRaisesRegex(MissingAPIKeyError, "ANTHROPIC_API_KEY"):
                ask("Como checar?", [])

    @patch("src.agent.core.urllib.request.urlopen")
    def test_ask_sends_context_and_returns_response(self, urlopen):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(
            {"content": [{"text": "Resposta de teste"}]}
        ).encode("utf-8")
        urlopen.return_value = response

        with patch("src.agent.core.API_KEY", "test-key"):
            result = ask("Como checar?", [KNOWLEDGE_BASE[2]])

        self.assertEqual(result, "Resposta de teste")
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertIn("[Método SIFT]", payload["messages"][0]["content"])
        self.assertEqual(request.get_header("X-api-key"), "test-key")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 60)

    @patch("src.agent.core.urllib.request.urlopen")
    def test_ask_converts_http_error(self, urlopen):
        from urllib.error import HTTPError
        from io import BytesIO

        urlopen.side_effect = HTTPError(
            "https://api.anthropic.com/v1/messages",
            401,
            "Unauthorized",
            {},
            BytesIO(b"invalid key"),
        )

        with patch("src.agent.core.API_KEY", "test-key"):
            with self.assertRaisesRegex(AnthropicAPIError, "Erro da API \\(401\\)"):
                ask("Como checar?", [])

    @patch("api.retrieve", return_value=[])
    @patch(
        "api.ask",
        side_effect=AnthropicAPIError(401, "invalid x-api-key"),
    )
    def test_invalid_key_returns_actionable_api_error(self, _ask, _retrieve):
        with self.assertRaises(HTTPException) as caught:
            api.perguntar(api.Pergunta(pergunta="Como checar?"))

        self.assertEqual(caught.exception.status_code, 502)
        self.assertIn("chave válida", caught.exception.detail)

    @patch("api.retrieve", return_value=[])
    @patch("api.ask", side_effect=MissingAPIKeyError("missing key"))
    def test_missing_key_returns_configuration_error(self, _ask, _retrieve):
        with self.assertRaises(HTTPException) as caught:
            api.perguntar(api.Pergunta(pergunta="Como checar?"))

        self.assertEqual(caught.exception.status_code, 503)
        self.assertIn(".env", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
