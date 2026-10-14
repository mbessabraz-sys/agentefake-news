"""
API do Assistente de Fake News (FastAPI)

Instalar:  pip install fastapi uvicorn anthropic scikit-learn
Rodar:     uvicorn api:app --reload
Abrir:     http://localhost:8000
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from fake_news_rag import ask, retrieve

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
    resposta = ask(body.pergunta, chunks)
    return {"resposta": resposta, "fontes": fontes}