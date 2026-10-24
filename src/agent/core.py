import json
import urllib.error
import urllib.request
from collections.abc import Sequence

from config.settings import API_KEY, MODEL
from src.agent.prompts import SYSTEM_PROMPT
from src.agent.state import KnowledgeChunk


class MissingAPIKeyError(RuntimeError):
    """Raised when the Anthropic API key is not configured."""


class AnthropicAPIError(RuntimeError):
    def __init__(self, status_code: int, response_body: str) -> None:
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(f"Erro da API ({status_code}): {response_body}")


def ask(pergunta: str, chunks: Sequence[KnowledgeChunk]) -> str:
    contexto = "\n\n".join(
        f"[{chunk['fonte']}]\n{chunk['texto']}" for chunk in chunks
    ) or "(vazio)"
    if not API_KEY:
        raise MissingAPIKeyError("ANTHROPIC_API_KEY não configurada.")
    payload = {
        "model": MODEL,
        "max_tokens": 800,
        "system": SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": f"CONTEXTO:\n{contexto}\n\nPERGUNTA: {pergunta}",
            }
        ],
    }
    request = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        try:
            error_body = error.read().decode("utf-8")
        finally:
            error.close()
        raise AnthropicAPIError(error.code, error_body) from error
    return data["content"][0]["text"]