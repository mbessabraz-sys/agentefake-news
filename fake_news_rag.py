"""Compatibilidade com os imports públicos da implementação monolítica."""

from src.agent.core import ask
from src.tools.search import retrieve

__all__ = ["ask", "retrieve"]


if __name__ == "__main__":
    from src.main import main

    main()
