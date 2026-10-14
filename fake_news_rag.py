"""
Assistente de Fake News com RAG - versão SEM dependências externas.
Usa só a biblioteca padrão do Python (roda em qualquer computador).

- Servidor: http.server
- Retrieval: TF-IDF implementado à mão
- Generation: API da Anthropic via HTTP direto

Rodar (PowerShell, na pasta dos arquivos):
    $env:ANTHROPIC_API_KEY="apikey_011Ko244jnqo7XnTgWVuyCPb"
    python app.py
Abrir: http://localhost:8000
"""
import json
import math
import os
import re 
import unicodedata
import urllib.error
import urllib.request
from collections import Counter
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

MODEL = "claude-sonnet-5-5"
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------
# 1) BASE DE CONHECIMENTO
# ---------------------------------------------------------------
KNOWLEDGE_BASE = [
    {"fonte": "Conceitos",
     "texto": "Fake news é conteúdo falso ou enganoso apresentado como se fosse notícia "
              "verdadeira. Pesquisadores preferem o termo 'desordem informacional', que "
              "separa: misinformation (informação falsa compartilhada sem intenção de "
              "causar dano), disinformation (falsa e criada de propósito para enganar) e "
              "malinformation (informação verdadeira usada para causar dano, como "
              "vazamento de dados privados)."},
    {"fonte": "Sinais de alerta",
     "texto": "Sinais comuns de fake news: título sensacionalista em caixa alta, apelo "
              "forte à emoção (raiva, medo, indignação), ausência de autor, data ou "
              "fonte citada, erros de português, pedido para 'compartilhar urgente', "
              "e site desconhecido com endereço parecido com o de um veículo conhecido."},
    {"fonte": "Método SIFT",
     "texto": "Método SIFT, de Mike Caulfield: Stop (pare antes de compartilhar), "
              "Investigate the source (investigue quem publicou), Find better coverage "
              "(procure cobertura em outros veículos confiáveis) e Trace claims "
              "(rastreie a afirmação, imagem ou citação até a origem)."},
    {"fonte": "Leitura lateral",
     "texto": "Leitura lateral é abrir novas abas e pesquisar sobre a fonte, em vez de "
              "só ler a própria página. Verificadores profissionais fazem isso: "
              "descobrem quem está por trás do site, qual o histórico dele e o que "
              "outras fontes dizem sobre ele."},
    {"fonte": "Imagens e vídeos",
     "texto": "Para checar imagens, use busca reversa (Google Lens, TinEye) e veja se a "
              "foto é antiga ou de outro contexto. Para vídeos, extraia quadros e busque "
              "a origem. Fique atento a deepfakes: rosto com bordas estranhas, piscar "
              "irregular, voz dessincronizada. Imagens geradas por IA podem ter mãos, "
              "textos e reflexos incoerentes."},
    {"fonte": "Agências de checagem",
     "texto": "No Brasil, agências de checagem conhecidas incluem Aos Fatos, Agência "
              "Lupa, Projeto Comprova, Fato ou Fake (g1) e Boatos.org. Antes de "
              "compartilhar, pesquise o tema nesses sites."},
    {"fonte": "Vieses cognitivos",
     "texto": "Caímos em fake news por viés de confirmação (acreditamos no que "
              "reforça o que já pensamos), efeito de repetição (o que vemos muitas "
              "vezes parece verdadeiro) e pelas bolhas dos algoritmos de redes sociais."},
]

SYSTEM_PROMPT = """Você é um assistente educativo sobre fake news e desinformação.
Responda SOMENTE com base no CONTEXTO fornecido. Se o contexto não cobrir a pergunta,
diga que não tem informação suficiente na base. Cite as fontes entre colchetes,
ex: [Método SIFT]. Você não declara se uma notícia específica é verdadeira ou falsa:
você ensina o método e indica como o usuário pode verificar. Responda em português."""


# ---------------------------------------------------------------
# 2) INDEXAÇÃO: TF-IDF feito à mão
# ---------------------------------------------------------------
def tokenizar(texto):
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return [t for t in re.findall(r"\w+", texto) if len(t) > 2]


N = len(KNOWLEDGE_BASE)
contagens = [Counter(tokenizar(d["texto"])) for d in KNOWLEDGE_BASE]
df = Counter()
for c in contagens:
    df.update(c.keys())
idf = {t: math.log((N + 1) / (df[t] + 1)) + 1 for t in df}


def vetor(contagem):
    return {t: n * idf[t] for t, n in contagem.items() if t in idf}


def norma(v):
    return math.sqrt(sum(x * x for x in v.values())) or 1.0


doc_vecs = [vetor(c) for c in contagens]
doc_norms = [norma(v) for v in doc_vecs]


# ---------------------------------------------------------------
# 3) RETRIEVAL: similaridade de cosseno
# ---------------------------------------------------------------
def retrieve(pergunta, k=3):
    qv = vetor(Counter(tokenizar(pergunta)))
    qn = norma(qv)
    scores = []
    for i, dv in enumerate(doc_vecs):
        dot = sum(w * dv.get(t, 0) for t, w in qv.items())
        scores.append(dot / (qn * doc_norms[i]))
    top = sorted(range(N), key=lambda i: scores[i], reverse=True)[:k]
    return [KNOWLEDGE_BASE[i] for i in top if scores[i] > 0]


# ---------------------------------------------------------------
# 4) GENERATION: chamada HTTP direta à API da Anthropic
# ---------------------------------------------------------------
def ask(pergunta, chunks):
    contexto = "\n\n".join(f"[{c['fonte']}]\n{c['texto']}" for c in chunks) or "(vazio)"
    if not API_KEY:
        raise RuntimeError("apikey_011Ko244jnqo7XnTgWVuyCPb")
    payload = {
        "model": MODEL,
        "max_tokens": 800,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user",
                      "content": f"CONTEXTO:\n{contexto}\n\nPERGUNTA: {pergunta}"}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={"x-api-key": API_KEY,
                 "anthropic-version": "2023-06-01",
                 "content-type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Erro da API ({e.code}): {e.read().decode('utf-8')}")
    return data["content"][0]["text"]


# ---------------------------------------------------------------
# 5) SERVIDOR WEB
# ---------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def _responder(self, status, corpo, tipo):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length",    str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            html = (BASE_DIR / "index.html").read_bytes()
            self._responder(200, html, "text/html; charset=utf-8")
        else:
            self._responder(404, b"Nao encontrado", "text/plain")

    def do_POST(self):
        if self.path != "/perguntar":
            return self._responder(404, b"Nao encontrado", "text/plain")
        try:
            tamanho = int(self.headers.get("Content-Length", 0))
            pergunta = json.loads(self.rfile.read(tamanho))["pergunta"]
            chunks = retrieve(pergunta)
            resposta = ask(pergunta, chunks)
            corpo = json.dumps({"resposta": resposta,
                                "fontes": [c["fonte"] for c in chunks]})
            self._responder(200, corpo.encode("utf-8"), "application/json")
        except Exception as e:
            print("Erro:", e)
            self._responder(500, json.dumps({"erro": str(e)}).encode("utf-8"),
                            "application/json")


if __name__ == "__main__":
    if not API_KEY:
        print("apikey_011Ko244jnqo7XnTgWVuyCPb")
    print("Servidor rodando em http://localhost:8000 (Ctrl+C para parar)")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
