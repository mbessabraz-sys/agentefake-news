from src.agent.state import KnowledgeChunk
from src.memory.vector_store import search


def retrieve(pergunta: str, k: int = 3) -> list[KnowledgeChunk]:
    return search(pergunta, k)
