import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

MODEL = "claude-sonnet-5-5"
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
HOST = "127.0.0.1"
PORT = 8000