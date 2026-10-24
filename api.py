"""API FastAPI do assistente de fake news."""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from src.agent.core import AnthropicAPIError, MissingAPIKeyError, ask
from src.tools.search import retrieve

app = FastAPI(title="Assistente de Fake News (RAG)")
BASE_DIR = Path(__file__).parent


class Pergunta(BaseModel):
    pergunta: str


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/perguntar")
def perguntar(body: Pergunta):
    chunks = retrieve(body.pergunta)
    fontes = [c["fonte"] for c in chunks]
    try:
        resposta = ask(body.pergunta, chunks)
    except MissingAPIKeyError as error:
        raise HTTPException(
            status_code=503,
            detail="Configure ANTHROPIC_API_KEY no arquivo .env e reinicie a API.",
        ) from error
    except AnthropicAPIError as error:
        if error.status_code == 401:
            detail = (
                "A Anthropic rejeitou a API_KEY (401). Confira se o .env contém "
                "uma chave válida da Anthropic e reinicie a API."
            )
        else:
            detail = (
                f"A API da Anthropic retornou HTTP {error.status_code}. "
                "Confira sua conta e tente novamente."
            )
        raise HTTPException(status_code=502, detail=detail) from error
    return {"resposta": resposta, "fontes": fontes}