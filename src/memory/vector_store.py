import math
import re
import unicodedata
from collections import Counter

from src.agent.state import KnowledgeChunk
from src.tools.database import KNOWLEDGE_BASE


def tokenizar(texto: str) -> list[str]:
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )
    return [token for token in re.findall(r"\w+", texto) if len(token) > 2]


N = len(KNOWLEDGE_BASE)
contagens = [Counter(tokenizar(chunk["texto"])) for chunk in KNOWLEDGE_BASE]
df: Counter[str] = Counter()
for contagem in contagens:
    df.update(contagem.keys())
idf = {token: math.log((N + 1) / (df[token] + 1)) + 1 for token in df}


def vetor(contagem: Counter[str]) -> dict[str, float]:
    return {
        token: quantidade * idf[token]
        for token, quantidade in contagem.items()
        if token in idf
    }


def norma(vector: dict[str, float]) -> float:
    return math.sqrt(sum(valor * valor for valor in vector.values())) or 1.0


doc_vecs = [vetor(contagem) for contagem in contagens]
doc_norms = [norma(vector) for vector in doc_vecs]


def search(query: str, k: int = 3) -> list[KnowledgeChunk]:
    query_vector = vetor(Counter(tokenizar(query)))
    query_norm = norma(query_vector)
    scores = []
    for document_vector, document_norm in zip(doc_vecs, doc_norms):
        dot_product = sum(
            weight * document_vector.get(token, 0)
            for token, weight in query_vector.items()
        )
        scores.append(dot_product / (query_norm * document_norm))

    top_indices = sorted(range(N), key=lambda i: scores[i], reverse=True)[:k]
    return [
        KNOWLEDGE_BASE[index]
        for index in top_indices
        if scores[index] > 0
    ]
